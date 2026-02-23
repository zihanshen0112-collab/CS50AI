import sys

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        _, _, w, h = draw.textbbox((0, 0), letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        for var in self.crossword.variables:
        # Get all words in current domain
            words_to_remove = []
            for word in self.domains[var]:
                # Check if word length matches variable length
                if len(word) != var.length:
                    words_to_remove.append(word)
            
            # Remove inconsistent words
            for word in words_to_remove:
                self.domains[var].remove(word)

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        revised = False
    
        # Check if x and y overlap
        overlap = self.crossword.overlaps[x, y]
        if overlap is None:
            return revised
        
        i, j = overlap  # i: index in x, j: index in y
        
        # Find values to remove from x's domain
        words_to_remove = []
        for word_x in self.domains[x]:
            # Check if there's any word_y that matches at overlap
            has_match = False
            for word_y in self.domains[y]:
                if word_x[i] == word_y[j]:
                    has_match = True
                    break
            
            if not has_match:
                words_to_remove.append(word_x)
        
        # Remove inconsistent values
        for word_x in words_to_remove:
            self.domains[x].remove(word_x)
            revised = True
        
        return revised

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        queue = []
        if arcs is None:
            # Add all arcs (both directions)
            for v1 in self.crossword.variables:
                for v2 in self.crossword.neighbors(v1):
                    queue.append((v1, v2))
        else:
            queue = list(arcs)
        
        # Process queue
        while queue:
            x, y = queue.pop(0)
            
            # Revise x with respect to y
            if self.revise(x, y):
                # Check if domain became empty
                if len(self.domains[x]) == 0:
                    return False
                
                # Add all neighbors of x (except y) back to queue
                for z in self.crossword.neighbors(x):
                    if z != y:
                        queue.append((z, x))
        
        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        for var in self.crossword.variables:
            if var not in assignment:
                return False
        return True

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        for var, word in assignment.items():
            if len(word) != var.length:
                return False
    
        # Check 2: All words are distinct
        words = list(assignment.values())
        if len(words) != len(set(words)):
            return False
        
        # Check 3: All overlaps are consistent
        for v1 in assignment:
            for v2 in assignment:
                if v1 == v2:
                    continue
                
                overlap = self.crossword.overlaps[v1, v2]
                if overlap is not None:
                    i, j = overlap
                    if assignment[v1][i] != assignment[v2][j]:
                        return False
        
        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        neighbors = [n for n in self.crossword.neighbors(var) 
                 if n not in assignment]
    
        # If no unassigned neighbors, return all values in any order
        if not neighbors:
            return list(self.domains[var])
        
        # Calculate conflicts for each value
        value_conflicts = []
        for value in self.domains[var]:
            conflicts = 0
            
            for neighbor in neighbors:
                overlap = self.crossword.overlaps[var, neighbor]
                if overlap is None:
                    continue
                
                i, j = overlap
                
                # Count how many values in neighbor's domain are eliminated
                for neighbor_val in self.domains[neighbor]:
                    if neighbor_val[j] != value[i]:
                        conflicts += 1
            
            value_conflicts.append((value, conflicts))
        
        # Sort by number of conflicts (ascending)
        value_conflicts.sort(key=lambda x: x[1])
        
        # Return just the values in order
        return [vc[0] for vc in value_conflicts]

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        unassigned = [var for var in self.crossword.variables 
                  if var not in assignment]
    
        if not unassigned:
            return None
        
        # MRV: Minimum Remaining Values
        best_var = unassigned[0]
        min_remaining = len(self.domains[best_var])
        
        for var in unassigned[1:]:
            remaining = len(self.domains[var])
            
            if remaining < min_remaining:
                best_var = var
                min_remaining = remaining
            elif remaining == min_remaining:
                # Tie-break by degree (number of neighbors)
                if len(self.crossword.neighbors(var)) > len(self.crossword.neighbors(best_var)):
                    best_var = var
        
        return best_var

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        if self.assignment_complete(assignment):
            return assignment
    
        # Select unassigned variable
        var = self.select_unassigned_variable(assignment)
        
        # Try values in order
        for value in self.order_domain_values(var, assignment):
            # Add value to assignment
            assignment[var] = value
            
            # Check if consistent
            if self.consistent(assignment):
                # Recursive call
                result = self.backtrack(assignment)
                if result is not None:
                    return result
            
            # Remove value (backtrack)
            del assignment[var]
        
        # No solution found
        return None


def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
