# fish-udacity-capstone
Repository for the capstone project of the full stack developer course on Udacity


Ideas for service - Video Game store catalog api

Models - 
  Game - 
    - name
    - genre
    - console
    - productId
  Console -
    - name
    - Company
    - productId
  Bundle - (stretch goal)
    - name
    - productIds (must be in stock)
    - bundleId
  Products -
    - productId
    - quantity
    - price
    
Endpoints -
   getGame
   getConsole
   getBundle
   getProducts
   getProducts/<productId>
  
  Post Put Delete for all above


<H1>Game Store API</H1>
<h2>Description</h2>
The purpose of this API is to act as a basic backend for a video game store. The Api will allow users to add new 
games and consoles tp the inventory and keep track of the quantity and price of the items.
<h2>Set up</h2>
<ul> 
<li>set up virtual environment if you wish</li>
<li>run pip install -r requirements.txt</li>
<li>make sure you have a database on your local machine that has a database titled game_store (nothing needs to be in it to start)</li>
<li>run python -m app to start the api</li>
  
</ul>