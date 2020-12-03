# About

This is project repository of *chattings.com* . This is messanger to communicate with people, sharing files, creating groups  with common interests.

# Install

Follow steps below to set up this repository on your computer

**Step 0**. Prepare folder where you will work

**Step 1**. Clone repository 
```
$ git clone https://github.com/whyme0/Chattings.git
```

**Step 2**. Create new python virtual enviroment and activate it.
```
$ python -m venv venv
$ source venv/Scripts/activate
```

**Step 3**. Go to repository and install pip requirements
```
$ cd Chattings
$ pip install -r requirements.txt
```

**Step 4**. Add file named *.env* (with content like below) to project *settings* folder:
```
SECRET_KEY=your_django_secret_key

default_db_password=your_db_password
default_db_host=your_db_host
default_db_name=your_db_name
default_db_user=your_db_user

EMAIL_HOST_USER=your_email_address
EMAIL_HOST_PASSWORD=your_email_password
```

**Step 5**. A few must-haves in django shell
```
python .\manage.py shell
...

>>> from django.contrib.contenttypes.models import ContentType
>>> from django.contrib.auth.models import Permission
>>> from apps.users.models import Profile

>>> content_type = ContentType.objects.get_for_model(Profile)
>>> Permission.objects.create(
    codename='can_login',
    name='Can login to site',
    content_type=content_type)
>>> exit()
```

**Step 6**. Make sure that everything work as expected by running tests
```
python .\manage.py test
```

After, tests you should see OK status.
