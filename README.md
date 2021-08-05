<H1>Pet Check In API</H1>
<h2>Description</h2>
The purpose of this API is to act as a basic backend for managing owners, pets and appointments for a vet. 
<h2>To run API locally</h2>
<ul> 
    <li>set up virtual environment if you wish</li>
    <li>run pip install -r requirements.txt</li>
    <li>make sure you have a database on your local machine that has a database titled pet_checkin (nothing needs to be in it to start)</li>
    <li>also make sure that your database is setup with a user test with a password test</li>
    <li>Execute 'source setup.sh' to set up environment variables</li>
    <li>run python -m app to start the api</li>
</ul>

<h2>Models</h2>
<h3>Owner</h3>
<ul>
    <li>id (key)</li>
    <li>name (required)</li>
    <li>phone (required)</li>
</ul>
<h3>Pet</h3>
<ul>
    <li>id (key)</li>
    <li>name (required)</li>
    <li>species (required)</li>
    <li>breed</li>
</ul>
<h3>Appointment</h3>
<ul>
    <li>id (key)</li>
    <li>pet_id (required)</li>
    <li>owner_id (required)</li>
    <li>time (required)</li>
    <li>date (required)</li>
</ul>

All of the models have GET, POST, PUT and DELETE functionality

<h3>Endpoints</h3>
For each model, there are two endpoints
<ol>
    <li>/{model name (plural)}</li>
    which supports:    
    <ul>
        <li>GET: gets all of the items of the specified model</li>
        <li>POST: adds a new item to the specified model</li>
    </ul>
    <li>/{model name (plural)}/{id-number}</li>
    which supports:    
    <ul>
        <li>GET: gets the item with the id passed in from the specified model</li>
        <li>PUT: updates an item in the specified model</li>
        <li>DELETE: deletes an item in the specified model</li>
    </ul>
</ol>

<h3>Authorization</h3>
All endpoints need authorization, this can be done by passing in JWT tokens into the header of requests

There are two main roles, vet-admins who can perform all requests and vet-techs who can do everything but delete requests

<h3>Unit tests</h3>
Make sure the database you are using has a database titled pet_checkin_test

Make sure to have run `source setup.sh` to load the environment variables

With that you just need to execute `python -m test_owner` to run a test, no other set up needed