# Parser1
I decided to write a static parser for apple electronics stores. The parser will be automatically updated every 3 days and plot price changes for each model + write data to excel (so far only there).
The project is almost complete, I did not make functionality for the iPad and Apple Watch because it takes a very long time to write a normal parser, and I just wanted to get acquainted with the basics of parsing.
It remains only to slightly edit the function of displaying changes in product prices and write a short instruction and explanation of the work done. Next, it is planned to write a parser for a dynamic site, but using orm (alchemy).

Approximate scheme of the project
![img_1.png](Documentation/img_1.png)


First of all we use command /start (to run tg bot). 
![img_2.png](Documentation/img_2.png)

After this command username and id automatically recorded to "User" table
![img_3.png](Documentation/img_3.png)

You can change your name or db refresh using "settings" button
![img_4.png](Documentation/img_4.png)

Also, bot send messages about products changed price from "my_list"
![img_5.png](Documentation/img_5.png)

Buttons Instr and Ab. shops just give an information about they (I don't add full description)
![img_6.png](Documentation/img_6.png)

User can get exel file with full information from db
![img_7.png](Documentation/img_7.png)
![img_8.png](Documentation/img_8.png)

Searching is a main Kb, here we can find the product we are interested in, add it in "my_list"
![img_9.png](Documentation/img_9.png)

For example
![img_10.png](Documentation/img_10.png)

In my list we can see all our goods
![img_11.png](Documentation/img_11.png)

We can delete them from list, on/off notice (price change) for each product. All changes confirm after "confirm" button.
Also, we can see graphics of price changing for each product.
![img_12.png](Documentation/img_12.png)