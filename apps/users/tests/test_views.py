from datetime import timedelta

from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission
from django.test import TestCase
from django.urls import reverse
from bs4 import BeautifulSoup
from django.core import mail


from ..models import Profile, EmailVerification, PasswordRecovery
from .. import views
from ..utils import force_confirm_email


class TestLoginView(TestCase):
    def setUp(self):
        content_type = ContentType.objects.get_for_model(Profile)
        can_login_perm = Permission.objects.create(
            codename='can_login',
            name='Can login to site',
            content_type=content_type,
        )
        self.user1.user_permissions.add(can_login_perm)
    
    @classmethod
    def setUpTestData(cls):
        # user with can_login permission
        cls.user1 = Profile.objects.create_user(
            username='temp1',
            email='temp1@mail.com',
            password='hardpwd123',
        )
        # user without can_login permission
        cls.user2 = Profile.objects.create_user(
            username='temp2',
            email='temp2@mail.com',
            password='hardpwd123',
        )


    def test_basics(self):
        """
        Check basic properties such as
        status_code, page title, view.
        """
        response = self.client.get(reverse('users:login'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.func.view_class, views.UserLoginView)
        
        title = BeautifulSoup(response.content, features='html.parser').find('title').getText().strip().replace('\n', '')
        self.assertEqual(title, 'Login \ Chattings')
    
    def test_login(self):
        """
        Checks that view authenticate and login user to site.
        """
        response = self.client.post(reverse('users:login'), data={
            'username': 'username',
            'password': '12345678',
        })
        self.assertFalse(response.wsgi_request.user.is_authenticated)

        response = self.client.post(reverse('users:login'), data={
            'username': 'temp1',
            'password': 'hardpwd123',
        })
        self.assertTrue(response.wsgi_request.user.is_authenticated)

        # And check that we can login with email
        self.client.logout()
        response = self.client.post(reverse('users:login'), data={
            'username': 'temp1@mail.com',
            'password': 'hardpwd123'
        })
        self.assertTrue(response.wsgi_request.user.is_authenticated)
    
    def test_field_errors(self):
        """
        Checks that field errors shows in form as expected.
        """
        # For username field
        response = self.client.post(reverse('users:login'), data={
            'username': 'username_that_not_exist',
            'password': '11111111',
        })
        error = BeautifulSoup(response.content, 'html.parser').find('p', 'username-error').text

        self.assertEqual(error, 'User with this username doesn\'t exist.')

        # For password field
        response = self.client.post(reverse('users:login'), data={
            'username': 'temp1',
            'password': '11111111',
        })
        error = BeautifulSoup(response.content, 'html.parser').find('p', 'non-field-error').text

        self.assertEqual(error, 'Enter correct password.')
    
    def test_email_verification_for_login(self):
        """
        Checks that if user haven't permission 'can_login'
        (particularly user not confirm his email entered
        in user registration form) django show error message
        with link for resending email verification.
        """
        # self.user2 haven't permission 'can_login'
        response = self.client.post(reverse('users:login'), data={
            'username': 'temp2',
            'password': 'hardpwd123',
        }, follow=True)
        soup = BeautifulSoup(response.content, 'html.parser')
        error = soup.find('p', 'email-not-confirmed')
        
        resend_email_link = soup.find('a', 'resend-email-link')
        expected_email_link = (f'{reverse("users:resend_confirmation_email")}'
            f'?redirect_to={reverse("users:login")}&username=temp2')

        self.assertEqual(error.text, 'Confirm your email to login.')
        self.assertEqual(resend_email_link['href'], expected_email_link)


class TestRegistrationView(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = Profile.objects.create_user(
            username='temp1',
            email='temp1@mail.com',
            password='hardpwd123',
        )
    
    def test_basics(self):
        """
        Check basic properties such as
        status_code, page title, view.
        """
        response = self.client.get(reverse('users:registration'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.func.view_class, views.UserRegistrationView)
        
        title = BeautifulSoup(response.content, features='html.parser').find('title').getText().strip().replace('\n', '')
        self.assertEqual(title, 'Registration \ Chattings')
    
    def test_registration(self):
        """
        Checks that view really create user and
        send email confirmation letter.
        """
        # Make sure that specific user doesn't exist
        # before registration
        with self.assertRaises(Profile.DoesNotExist):
            Profile.objects.get(username='temp2')
        self.assertEqual(len(mail.outbox), 0)
        response = self.client.post(reverse('users:registration'), data={
            'username': 'temp2',
            'email': 'temp2@mail.com',
            'password1': 'hardpwd123',
            'password2': 'hardpwd123',
        }, follow=True)

        # And after registration, the user is created
        created_user = Profile.objects.get(username='temp2')
        token = created_user.email_verification.token

        # Make sure that client see success message
        soup = BeautifulSoup(response.content, 'html.parser')
        success_msg = soup.find('p', 'success-registration')

        self.assertEqual(
            success_msg.text,
            ('We sent email confirmation link to your'
            ' email box. (Don\'t forget to check spam box)')
        )

        # Check for sent email.
        
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Follow this link to confirm your email address:', mail.outbox[0].body)
        
    
    def test_registration_errors(self):
        """
        Checks that client see fields errors
        if data enetered wrong.
        """
        response = self.client.post(reverse('users:registration'), data={
            'username': 'temp1',
            'email': 'temp1@x',
            'password1': 'pwd123',
            'password2': '123pwd',
        }, follow=True)

        soup = BeautifulSoup(response.content, 'html.parser')
        username_error = soup.find('p', 'username-error').text
        email_error = soup.find('p', 'email-error').text
        password2_error = soup.find('p', 'password2-error').text

        self.assertEqual(username_error, 'A user with that username already exists.')
        self.assertEqual(email_error, 'Enter a valid email address.')
        self.assertEqual(password2_error, 'The two password fields didn’t match.')

        response = self.client.post(reverse('users:registration'), data={
            'username': '&*',
            'email': 'temp1@mail.com',
            'password1': '123',
            'password2': '123',
        }, follow=True)

        soup = BeautifulSoup(response.content, 'html.parser')
        username_error = soup.find('p', 'username-error').text
        email_error = soup.find('p', 'email-error').text
        password2_error = soup.find_all('p', 'password2-error')

        self.assertEqual(username_error, 'Enter valid username. This value may contain only letters, numbers, and -/_ characters.')
        self.assertEqual(email_error, 'User with this Email already exists.')
        self.assertEqual(password2_error[0].text, 'This password is too short. It must contain at least 8 characters.')
        self.assertEqual(password2_error[1].text, 'This password is too common.')
        self.assertEqual(password2_error[2].text, 'This password is entirely numeric.')


class TestEmailConfirmationView(TestCase):
    def setUp(self):
        content_type = ContentType.objects.get_for_model(Profile)
        self.can_login_perm = Permission.objects.create(
            codename='can_login',
            name='Can login to site',
            content_type=content_type,
        )

    @classmethod
    def setUpTestData(cls):
        cls.test_user = Profile.objects.create_user(
            username='temp1',
            email='temp1@m.co',
            password='hardpwd123',
        )
    
    def test_basics(self):
        """
        Check basic properties such as
        status_code, page title, view.
        """
        random_token = 'abcd453'
        response = self.client.get(reverse('users:email_confirmation', kwargs={
            'token': 'randomEmailVerification5356',
        }))
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.func.view_class, views.EmailConfirmationView)

        title = BeautifulSoup(response.content, 'html.parser').find('title').getText().strip().replace('\n', '')
        self.assertEqual(title, 'Email confirmation \ Chattings')
    
    def test_main_logic(self):
        """
        The verification algorithm is as follows:
        1. check that the user cannot log in without a verified mail
        2. verify email address with get method in view
        3. make sure that the user can log in, and the EmailVerification
           model for the associated user is removed
        """
        # PART 1
        self.assertFalse(self.test_user.has_perm('users.can_login'))
        response = self.client.post(reverse('users:login'), data={
            'username': self.test_user.username,
            'password': 'hardpwd123',
        })
        self.assertFalse(response.wsgi_request.user.is_authenticated)

        # PART 2
        response = self.client.get(reverse('users:email_confirmation', kwargs={
            'token': self.test_user.email_verification.token,
        }))

        self.assertIn(self.can_login_perm, self.test_user.user_permissions.all())
        soup = BeautifulSoup(response.content, 'html.parser')
        success_message = soup.find('p', 'email-confirmed')
        login_link = soup.find('a', 'login-link')

        self.assertEqual(success_message.text, 'Email successfully confirmed, now you can login.')
        self.assertEqual(login_link['href'], reverse('users:login'))

        # PART 3
        test_user = Profile.objects.get(pk=self.test_user.pk)
        self.assertTrue(test_user.has_perm('users.can_login'))
        
        response = self.client.post(reverse('users:login'), data={
            'username': self.test_user.username,
            'password': 'hardpwd123'
        })
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_errors(self):
        """
        Check that django display error in html template
        for client properly
        """
        response = self.client.get(reverse('users:email_confirmation', kwargs={
            'token': 'invalidEmailVerification31231323',
        }))

        soup = BeautifulSoup(response.content, 'html.parser')
        error_msg = soup.find('p', 'invalid-token')

        self.assertEqual(error_msg.text, 'Invalid token. Make sure your token is valid and not deleted.')


class TestResendEmailConfirmation(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.temp_user1 = Profile.objects.create_user(
            username='temp_user1',
            email='temp1@mail.co',
            password='hardpwd123',
        )

    
    def test_errors(self):
        """
        Check that with wrong data in url
        client see 404 error
        """
        response = self.client.get(reverse('users:resend_confirmation_email'))
        self.assertEqual(response.status_code, 404)

        response = self.client.get(
            reverse(
                'users:resend_confirmation_email',
            ),
            data={
                'redirect_to': reverse('users:login'),
                'username': 'wrong_username',
            }
        )
        self.assertEqual(response.status_code, 404)

    def test_view_logic(self):
        """
        Check that ResendEmailVerification truly
        resened email verification
        """
        # data to compare:
        token = self.temp_user1.email_verification.token
        creation_date = self.temp_user1.email_verification.creation_date
        expiration_date = self.temp_user1.email_verification.expiration_date
        response = self.client.get(
            reverse(
                'users:resend_confirmation_email',
            ),
            data={
                'redirect_to': reverse('users:login'),
                'username': 'temp_user1',
            },
            follow=True
        )
        self.temp_user1.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.view_name, 'users:login')
        self.assertNotEqual(token, self.temp_user1.email_verification.token)
        self.assertNotEqual(
            creation_date,
            self.temp_user1.email_verification.creation_date
        )
        self.assertNotEqual(
            expiration_date,
            self.temp_user1.email_verification.expiration_date
        )
        

class TestAskEmailPasswordRecoveryView(TestCase):
    def setUp(self):
        content_type = ContentType.objects.get_for_model(Profile)
        can_login_perm = Permission.objects.create(
            codename='can_login',
            name='Can login to site',
            content_type=content_type,
        )
        force_confirm_email(self.confirmed_u.email_verification.token)
        
    @classmethod
    def setUpTestData(cls):
        cls.confirmed_u = Profile.objects.create_user(
            username='temp1',
            email='temp1@mail.co',
            password='hardpwd123',
        )
        
        cls.notconfirmed_u = Profile.objects.create_user(
            username='temp2',
            email='temp2@mail.co',
            password='hardpwd123',
        )
    
    def test_basics(self):
        """
        Check basic properties such as
        status_code, page title, view.
        """
        response = self.client.get(reverse('users:perform_password_recovery'))
        title = BeautifulSoup(response.content, 'html.parser').find('title').getText().strip().replace('\n', '')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(title, 'Password Recovery \ Chattings')
        self.assertEqual(response.resolver_match.func.view_class, views.AskEmailForPasswordRecoveryView)

    def test_errors(self):
        """
        Check that view shows errors in template to client
        """
        response = self.client.post(
            reverse('users:perform_password_recovery'),
            data={'email': 'invalid@mail'},
            follow=True,
        )

        soup = BeautifulSoup(response.content, 'html.parser')
        err = soup.find('p', 'email-error').text

        self.assertEqual(err, 'Enter a valid email address.')

        response = self.client.post(
            reverse('users:perform_password_recovery'),
            data={'email': 'invalid@mail.co'},
            follow=True,
        )

        soup = BeautifulSoup(response.content, 'html.parser')
        err = soup.find('p', 'email-error').text

        self.assertEqual(err, 'User with this email doesn\'t exist.')
        
    def test_logic(self):
        """
        Check that the view is processed correctly.
        """
        self.client.force_login(self.confirmed_u)
        self.assertEqual(len(mail.outbox), 0)
        # password recovery model doesn't exist yet
        with self.assertRaises(PasswordRecovery.DoesNotExist):
            self.confirmed_u.password_recovery
        
        response = self.client.get(reverse('users:perform_password_recovery'))
        self.assertTrue(response.wsgi_request.user.is_authenticated)
        
        response = self.client.post(
            reverse('users:perform_password_recovery'),
            data={'email': 'temp1@mail.co'},
            follow=True,
        )
        self.confirmed_u.refresh_from_db()
        # client side:
        soup = BeautifulSoup(response.content, 'html.parser')
        success_message = soup.find('p', 'pwd-recovery-mail-sent').text
        self.assertEqual(success_message, 'Now check your email for password recovery message.')
        
        # server side:
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.wsgi_request.user.is_authenticated)
        self.assertIsNotNone(self.confirmed_u.password_recovery)
        self.assertEqual(response.resolver_match.func.view_class, views.AskEmailForPasswordRecoveryView)

        # check that the email message was sent
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Follow this link to continue password recovery', mail.outbox[0].body)


class TestPasswordResetView(TestCase):
    """
    Plan:
    * Test fundamental view behavior.
    * Test for expected errors
    * Test for main logic: view works as originally intended
    """
    def setUp(self):
        content_type = ContentType.objects.get_for_model(Profile)
        can_login_perm = Permission.objects.create(
            codename='can_login',
            name='Can login to site',
            content_type=content_type,
        )
        force_confirm_email(self.confirmed_u.email_verification.token)

    @classmethod
    def setUpTestData(cls):
        cls.confirmed_u = Profile.objects.create_user(
            username='temp1',
            email='temp1@mail.co',
            password='hardpwd123',
        )

        cls.notconfirmed_u = Profile.objects.create_user(
            username='temp2',
            email='temp2@mail.co',
            password='hardpwd123',
        )
        PasswordRecovery.objects.create(profile=cls.confirmed_u)
        PasswordRecovery.objects.create(profile=cls.notconfirmed_u)

    def test_basics(self):
        """
        Check basic properties such as
        status_code, page title, view.
        """
        response = self.client.get(
            reverse(
                'users:recover_password',
                kwargs={
                    'token': self.confirmed_u.password_recovery.token,
                },
            ),
            follow=True,
        )

        title = BeautifulSoup(response.content, 'html.parser').find('title').getText().strip().replace('\n', '')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(title, 'Password Recovery \ Chattings')
        self.assertEqual(response.resolver_match.func.view_class, views.PasswordResetView)
    
    def test_for_bad_request_errors(self):
        """
        This test check if token invalid then server will send
        BadRequest to the Browser.
        """
        # Invalid token:
        response = self.client.get(
            reverse(
                'users:recover_password',
                kwargs={
                    'token': 'invalid_token',
                },
            ),
            follow=True,
        )

        self.assertEqual(response.status_code, 400)

    def test_for_html_form_errors(self):
        """
        This test check if client entered invalid
        data to params then errors will be shown
        in template.
        """
        # PART 1
        response = self.client.post(
            reverse(
                'users:recover_password',
                kwargs={
                    'token': self.confirmed_u.password_recovery.token
                }
            ),
            data={
                'new_password1': '123',
                'new_password2': '123',
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        
        errors = BeautifulSoup(response.content, 'html.parser').find_all('p', 'field_error')
        
        self.assertEqual(errors[0].text, 'This password is too short. It must contain at least 8 characters.')
        self.assertEqual(errors[1].text, 'This password is too common.')
        self.assertEqual(errors[2].text, 'This password is entirely numeric.')

        # PART 2        
        response = self.client.post(
            reverse(
                'users:recover_password',
                kwargs={
                    'token': self.confirmed_u.password_recovery.token,
                }
            ),
            data={
                'new_password1': 'uiuiuiuiu',
                'new_password2': 'iuiuiuiui',
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        errors = BeautifulSoup(response.content, 'html.parser').find_all('p', 'field_error')

        self.assertEqual(errors[0].text, 'The two password fields didn’t match.')

    def test_for_success_recovery(self):
        """
        Test that with proper data user
        can recover password
        """
        self.assertTrue(self.confirmed_u.check_password('hardpwd123'))
        response = self.client.post(
            reverse(
                'users:recover_password',
                kwargs={
                    'token': self.confirmed_u.password_recovery.token,
                }
            ),
            data={
                'new_password1': 'goodPwd345',
                'new_password2': 'goodPwd345',
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.confirmed_u.refresh_from_db()

        with self.assertRaises(PasswordRecovery.DoesNotExist):
            self.confirmed_u.password_recovery

        self.assertFalse(self.confirmed_u.check_password('hardpwd123'))
        self.assertTrue(self.confirmed_u.check_password('goodPwd345'))

        self.assertEqual(response.resolver_match.func.view_class, views.UserLoginView)

        soup = BeautifulSoup(response.content, 'html.parser')
        success_msg = soup.find('p', 'success-pwd-reset')

        self.assertEqual(success_msg.text, 'Password changed. You can login now.')

    def test_for_success_recovery_and_email_confirmation(self):
        """
        Test that with proper data user can recover
        password and confirm email, if it not confirmed
        """
        self.assertFalse(self.notconfirmed_u.is_email_confirmed())
        self.assertTrue(self.notconfirmed_u.check_password('hardpwd123'))
        response = self.client.post(
            reverse(
                'users:recover_password',
                kwargs={
                    'token': self.notconfirmed_u.password_recovery.token,
                }
            ),
            data={
                'new_password1': 'goodPwd345',
                'new_password2': 'goodPwd345',
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.notconfirmed_u.refresh_from_db()

        self.assertTrue(self.notconfirmed_u.has_perm('users.can_login'))
        with self.assertRaises(PasswordRecovery.DoesNotExist):
            self.notconfirmed_u.password_recovery

        self.assertFalse(self.notconfirmed_u.check_password('hardpwd123'))
        self.assertTrue(self.notconfirmed_u.check_password('goodPwd345'))


class TestProfileLogoutView(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.u = Profile.objects.create_user(
            username='temp1',
            email='temp1@mail.co',
            password='hardpwd123',
        )
    
    def test_main(self):
        """Check that view works as expected"""
        self.client.force_login(self.u)
        response = self.client.get(
            '/test/',
        )
        self.assertTrue(response.wsgi_request.user.is_authenticated)

        response = self.client.get(
            reverse('users:logout'),
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.resolver_match.func.view_class, views.ProfileLogoutView)
        self.assertFalse(response.wsgi_request.user.is_authenticated)
    
    def test_login_required(self):
        """Check that if user not login then user can't logout"""
        response = self.client.get('/test/')
        self.assertFalse(response.wsgi_request.user.is_authenticated)

        response = response = self.client.get(
            reverse('users:logout'),
            follow=True
        )

        self.assertFalse(response.wsgi_request.user.is_authenticated)
        self.assertEqual(response.resolver_match.func.view_class, views.UserLoginView)


class TestProfileView(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.u = Profile.objects.create_user(
            username='temp1',
            email='temp1@mail.co',
            password='hardpwd123',
        )

    def test_fundamental_view_properties(self):
        """Testing title, templates, status code, etc."""
        response = self.client.get(
            reverse('users:profile', kwargs={'pk' : self.u.pk})
        )
        title = BeautifulSoup(response.content, features='html.parser').find('title').getText().strip().replace('\n', '')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.func.view_class, views.ProfileView)
        self.assertEqual(title, 'Profile №%d \\ Chattings' % self.u.id)


class TestProfileEditView(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.u = Profile.objects.create_user(
            username='temp1',
            email='temp1@mail.co',
            password='hardpwd123',
        )
    
    def setUp(self):
        content_type = ContentType.objects.get_for_model(Profile)
        can_login_perm = Permission.objects.create(
            codename='can_login',
            name='Can login to site',
            content_type=content_type,
        )
        force_confirm_email(self.u.email_verification.token)

    def test_basic(self):
        response = self.client.get(
            reverse('users:edit-profile'),
            follow=True,
        )
        self.assertEqual(response.resolver_match.func.view_class, views.UserLoginView)

        self.client.force_login(self.u)
        response = self.client.get(
            reverse('users:edit-profile'),
        )
        title = BeautifulSoup(response.content, features='html.parser').find('title').getText().strip().replace('\n', '')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.func.view_class, views.ProfileEditView)
        self.assertEqual(title, 'Profile Editing \ Chattings')
    
    def test_password_change_form_correctness(self):
        self.client.force_login(self.u)
        self.assertTrue(self.u.check_password('hardpwd123'))
        response = self.client.post(
            f'{reverse("users:edit-profile")}?form_type=change_password_form',
            data={
                'old_password': 'hardpwd123',
                'new_password1': 'newhardpwd123',
                'new_password2': 'newhardpwd123',
            },
            follow=True,
        )
        self.u.refresh_from_db()

        self.assertFalse(self.u.check_password('hardpwd123'))
        self.assertFalse(response.wsgi_request.user.is_authenticated)
        self.assertEqual(response.resolver_match.func.view_class, views.UserLoginView)
    
    # def test_password_change_form_errors(self):
    #     self.client.force_login(self.u)
    #     # PART 1
    #     response = self.client.post(
    #         f'{reverse("users:edit-profile")}?form_type=change_password_form',
    #         data={
    #             'old_password': 'somepwd123',
    #             'new_password1': '123',
    #             'new_password2': '123',
    #         },
    #         follow=True,
    #     )

    #     soup = BeautifulSoup(response.content, 'html.parser')

    #     errors = soup.find_all('p', 'field_error')

    #     self.assertEqual(errors[0].text, 'Your old password was entered incorrectly. Please enter it again.')
    #     self.assertEqual(errors[1].text, 'This password is too short. It must contain at least 8 characters.')
    #     self.assertEqual(errors[2].text, 'This password is too common.')
    #     self.assertEqual(errors[3].text, 'This password is entirely numeric.')

    #     # PART 2
    #     response = self.client.post(
    #         f'{reverse("users:edit-profile")}?form_type=change_password_form',
    #         data={
    #             'old_password': 'hardpwd123',
    #             'new_password1': 'somepwd123',
    #             'new_password2': 'somepwd321',
    #         }
    #     )
    #     soup = BeautifulSoup(response.content, 'html.parser')
    #     errors = soup.find_all('p', 'field_error')

    #     self.assertEqual(errors[0].text, 'The two password fields didn’t match.')


class TestPrivacySettingsFormHandlerView(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.u = Profile.objects.create_user(
            username='temp1',
            email='temp1@mail.co',
            password='hardpwd123',
        )
    
    def setUp(self):
        content_type = ContentType.objects.get_for_model(Profile)
        can_login_perm = Permission.objects.create(
            codename='can_login',
            name='Can login to site',
            content_type=content_type,
        )
        force_confirm_email(self.u.email_verification.token)
    
    def test_login_required(self):
        response = self.client.get(
            reverse('users:privacy-settings-form-handler'),
            follow=True
        )

        self.assertEqual(response.resolver_match.func.view_class, views.UserLoginView)
    
    def test_for_errors(self):
        self.client.force_login(self.u)
        response = self.client.get(
            reverse('users:privacy-settings-form-handler'),
        )

        self.assertEqual(response.status_code, 405)
    
    def test_view_for_correctness(self):
        old_data = {
            'is_email_public': self.u.privacy_settings.is_email_public,
            'is_username_public': self.u.privacy_settings.is_username_public,
            'is_date_joined_public': self.u.privacy_settings.is_date_joined_public,
        }

        self.client.force_login(self.u)
        response = self.client.post(
            reverse('users:privacy-settings-form-handler'),
            data={
                'is_email_public': True,
                'is_username_public': True,
                'is_date_joined_public': True
            }
        )
        self.u.privacy_settings.refresh_from_db()

        privacy_settings = self.u.privacy_settings
        self.assertNotEqual(
            privacy_settings.is_email_public,
            old_data['is_email_public'],
        )
        self.assertNotEqual(
            privacy_settings.is_username_public,
            old_data['is_email_public'],
        )
        self.assertNotEqual(
            privacy_settings.is_date_joined_public,
            old_data['is_email_public'],
        )

        new_data = {
            'is_email_public': privacy_settings.is_email_public,
            'is_username_public': privacy_settings.is_username_public,
            'is_date_joined_public': privacy_settings.is_date_joined_public,
        }

        for value in new_data.values():
            self.assertEqual(value, True)
