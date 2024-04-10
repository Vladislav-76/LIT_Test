# LIT_Test_Backend

This is a project that involves creating a RESTful API with Django.  
Authentication and authorization with additional user confirmation with an OTP code. Configuring Celery, Redis for message queues.

------------

#### Deploying the project.
The project is configured for easy local installation in Docker containers.  
After cloning the project, you can create an .env file from .env.sample to make settings different from the default ones.  
Command for building and running containers.  
`make up`

Five containers will be launched:
1. db (Postgress)
2. nginx
3. backend
4. worker
5. redis

Command for performing migrations, collecting statics and creating a superuser (email: admin@test.com, password: 123).  
`make build`

Project addresses:  
Admin: http://localhost:8000/admin/  
API documentation: http://localhost:8000/swagger/

------------
#### API description for user management and authorization.  
The project contains the Postman collection that contains the main endpoints with sample request bodies to test endpoints easier.
 
##### User creation
A user is created using a POST request to the address:  
http://localhost:8000/api/v1/auth/user/
An inactive user is created. A letter with an OTP code is sent to the email address specified during registration to confirm and activate the user.
Sending a letter is emulated. The letter is saved to the emails folder of the worker container.  
Command to view folder emails:  
`docker compose exec worker ls emails`  
Command to view the letter (replace the file name with the correct one):  
`docker compose exec worker head -n20 emails/20240402-162130-139799482503936.log`
 
##### User activation
User activation is performed by a POST request to the address:  
http://localhost:8000/api/v1/auth/user/activation/  
The lifetime of the code received in a letter is limited by the parameter in the project settings.  
If the combination of the user's email, code and time is valid the user is activated. Otherwise status 400 is returned. No additional information is provided for security reasons.

##### OTP refresh
You can receive a new OTP code at any time with a POST request:
http://localhost:8000/api/v1/auth/user/otp/
A letter with an OTP code is sent by email, old code now is invalid.

##### Receiving a token
Receiving a token is possible only after activation. The token is received using a POST request to the address with the combination of the user's email and OTP code:  
http://localhost:8000/api/v1/auth/jwt/create/
 
##### User management
User management requires authorization using a JWT token. Management is carried out at the address:  
http://localhost:8000/api/v1/auth/user/me/  
Implemented:
- view user data (GET)
- changing user data (PATCH)
- deleting a user (DELETE)
