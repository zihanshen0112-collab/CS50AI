# Planning
In a Knights and Knaves puzzle, each character is either a knight or a knave. 
A knight will always tell the truth while a knave will always lie. 
The  program is aiming to inference each character is a knight or knave based on several provided dialog for four Knights and  Knaves puzzle.

For the sake of solving the puzzle, 
the provided dialog should be translated into understanable laguge for the program using pre-defined logic connective  and put into the knowledge base as an input. 
Inaddition, the program is expected to output correct solusion for each puzzle.

# Analysis
The program innitally have all logic connective been defined using inheritaed classes in **logic.py**, which include `Not`, `And`, `Or`, `Implication` and `'Biconditional'`. `'Symble'`,letters used to represent a proposition, is also defined with the same method in the same document.
A method of enumerating all posisble modles, assignments of a truth value to every proposition, and check them with recursion is also predefined in **puzzle.py** made up by fuctions in **logic.py**. By doing this, it is able to test if the knowledge base entails the proposition which is the slusion of a puzzle and out put the correct answer.

The programer has to fill the knowledge base according to the provided dialoge between characters to make the code fuctioning, which is translating real world sentences to a type of language that this program is able to understand using the predefined logic connective.

As assuming all innitially provided code is correct, any possible errors can be solved by rechek the syntext and context translation that is filled into the knowledge base.

