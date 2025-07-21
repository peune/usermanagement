# A simple user management system
I tried to develop a user management system using docker-compose to manage micro-services.
I've never done this, so I ask several LLMs to help.
I end up with:
- Postgres to store users table
- Pgadmin to monitor the users if the user approval/reject works properly
- Fastapi used in making endpoints

To use it in your project just "mv your.env .env" and modify some element therein.

Right now
- There is a default Admin with login:admin@example.com and password:adminpassword
  - The users table stores, indeed, hashed password. So if you want to change the default password, just pass the new password to the function auth.get_password_hash(). Or create new user with new password then copy the hashed password from Pgadmin.
- User can register then wait for approval.
- Admin can approve or reject new users.
- User can ask for new password.

# Basic usage
- To start all services: docker-compose up -d --build
- To stop all services: docker-compose down
- To stop all services and remove all stored data: docker-compose down -v
    
