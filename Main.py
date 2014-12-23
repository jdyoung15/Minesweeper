from Tkinter import *
import random


class Application(Frame):
    """The Frame displaying the grid of tiles."""

    def __init__(self, height, width, mine_count, master):
        """Initializes the Frame."""

        Frame.__init__(self, master)
        self.height = height
        self.width = width
        self.mine_count = mine_count 
        self.MINE_VALUE = -1
        self.tiles = []
        self.create_tiles()


    def create_tiles(self):
        """Creates the grid of tiles, with dimensions self.height x 
        self.width. 

        """
        # Create blank tiles.
        for r in range(0, self.height):
            for c in range(0, self.width):
                tile = Button(self, image=blank)
                tile.bind("<Button-1>", self.handle_left_click)
                tile.bind("<Button-3>", self.handle_right_click)
                tile.grid(row=r, column=c)
                tile.row = r
                tile.column = c
                tile.blank = True
                tile.flag = False
                tile.value = 0
                self.tiles.append(tile)

        # Randomly assign mines to tiles.
        num_mines = self.mine_count
        while num_mines > 0:
            tile = random.choice(self.tiles)
            if self.is_mine(tile): 
                # Selected tile is already a mine. Skip.
                continue

            tile.value = self.MINE_VALUE
            num_mines -= 1

            # Update values of neighboring tiles.
            for n in self.find_neighbors(tile.row, tile.column):
                if not self.is_mine(n): 
                    n.value += 1
             

    def handle_left_click(self, event):
        """Called when a tile is clicked with the left mouse button."""
        self.reveal(event.widget)


    def handle_right_click(self, event):
        """Called when a tile is clicked with the right mouse button. Marks tile
        with a flag if previously blank or blank if previously flagged.

        """
        tile = event.widget
        if tile.flag:
            tile["image"] = blank
        else:
            tile["image"] = flag 
        tile.flag = not tile.flag


    def handle_double_click(self, event):
        """Called when player double-clicks a numbered tile. Uncovers all 
        neighboring non-mine squares.

        """
        tile = event.widget
        neighbors = self.find_neighbors(tile.row, tile.column)
        count_flags = 0
        for n in neighbors:
            if n.blank == True and n.flag == True:
                count_flags += 1

        # Double-click is only valid if tile's value equals number of flagged
        # neighboring tiles.
        if count_flags == tile.value:
            lost = []
            for n in neighbors:
                if self.is_mine(n) and not n.flag:
                    lost.append(n)
                elif not self.is_mine(n) and n.blank and n.flag:
                    self.change_tile(n, wrong)
    
            if len(lost) > 0:
                self.lose_game(lost)
                return

            for n in neighbors:
                if n.blank and not self.is_mine(n):
                    self.reveal(n)


    def reveal(self, tile):
        """Determines how TILE should be dealt with based on whether it contains
        a mine, has no neighboring mines, or has at least one neighboring mine.

        """
        # Check if mine tile.
        if self.is_mine(tile):
            self.lose_game([tile])

        # Check if empty tile.
        elif tile.value == 0:
            self.change_tile(tile, empty)
            tile["state"] = DISABLED
            for n in self.find_neighbors(tile.row, tile.column):
                if n.blank:
                    self.reveal(n)

        # Numbered tile.
        else:
            self.change_tile(tile, numbers[tile.value - 1])
            tile["state"] = DISABLED

        if self.check_win():
            self.win_game()


    def change_tile(self, tile, img):
        """Changes TILE to display new image IMG."""

        r = tile.row
        c = tile.column
        new_tile = Label(self, image=img)
        new_tile.row = r
        new_tile.column = c
        new_tile.blank = False
        new_tile.grid(row=r, column=c)
        new_tile["relief"] = SUNKEN
        if not self.is_mine(tile):
            new_tile.bind("<Double-Button-1>", self.handle_double_click)
            new_tile.value = tile.value
        self.tiles[self.width*r+c] = new_tile


    def find_neighbors(self, r, c):
        """Returns all tiles neighboring the tile at row r and column c."""

        nbr_coord = [ [r-1, c-1], [r-1, c], [r-1, c+1], [r, c+1], \
                      [r+1, c+1], [r+1, c], [r+1, c-1], [r, c-1]  ]  

        neighbors = []
        for r,c in nbr_coord:
            # Check if r and c are within table boundaries.
            if r >= 0 and r < self.height and c >= 0 and c < self.width: 
                neighbors.append(self.tiles[self.width*r+c])

        return neighbors
        

    def check_win(self):
        """Checks if the game has been won. This will be the case when the
        number of blank tiles is equal to the number of mines. 

        """
        count = 0
        for tile in self.tiles:
            if tile.blank:
                count += 1
        return count <= self.mine_count


    def win_game(self):
        """Called when the game is won. Flags all mine tiles, if the player 
        had not done so already.

        """
        for tile in self.tiles:
            if tile.blank and self.is_mine(tile):
                self.change_tile(tile, flag)


    def lose_game(self, mine_tiles):
        """Called when the game is lost. Reveals the location of all mines."""

        for tile in self.tiles:
            if self.is_mine(tile):
                self.change_tile(tile, mine)
            elif tile.blank:
                self.change_tile(tile, blank)

        for mine_tile in mine_tiles:
            self.change_tile(mine_tile, explode)


    def is_mine(self, tile):
        """Returns true if TILE is a mine, false otherwise."""

        return tile.value == self.MINE_VALUE



####################################################
#                   Global Methods                 #
####################################################

def exit():
    """Closes the application."""

    root.destroy()


def play(height, width, num_mines):
    """Starts a new game with the specified height, width, and number of mines."""

    global app
    app.destroy()
    app = Application(height, width, num_mines, root)
    app.pack(side=BOTTOM)
    app.mainloop()


def play_easy():
    """Starts a new game with a 9 x 9 tile grid and 10 mines."""

    play(9, 9, 10)


def play_medium():
    """Starts a new game with a 16 x 16 tile grid and 40 mines."""

    play(16, 16, 40)


def play_difficult():
    """Starts a new game with a 16 x 30 tile grid, and 99 mines."""

    play(16, 30, 99)



####################################################
#               Initializing the GUI               #
####################################################

root = Tk()
root.title('Minesweeper')

#Create menu.
menubar = Menu(root)

filemenu = Menu(menubar, tearoff=0)
filemenu.add_command(label="Exit", command=exit)
menubar.add_cascade(label="File", menu=filemenu)
root.config(menu=menubar)

playmenu = Menu(menubar, tearoff=0)
playmenu.add_command(label="Easy", command=play_easy)
playmenu.add_command(label="Medium", command=play_medium)
playmenu.add_command(label="Difficult", command=play_difficult)
menubar.add_cascade(label="Play", menu=playmenu)
root.config(menu=menubar)


#Load images.
empty = PhotoImage(file="images/empty.gif", width=20, height=20)
blank = PhotoImage(file="images/blank.gif", width=20, height=20)
mine = PhotoImage(file="images/mine.gif", width=20, height=20)
explode = PhotoImage(file="images/explode.gif", width=20, height=20)
wrong = PhotoImage(file="images/wrong.gif", width=20, height=20)
flag = PhotoImage(file="images/flag.gif", width=20, height=20)
numbers = [PhotoImage(file="images/number-%d.gif" % i, width=20, height=20) 
           for i in range(1, 8)]

app = Application(9, 9, 10, root)
app.pack(side=BOTTOM)
app.mainloop()
root.mainloop()
