from Tkinter import *
import random


class Application(Frame):
    """The Frame displaying the grid of tiles."""

    def __init__(self, height, width, mine_count, master):
        """Initialize the Frame."""

        Frame.__init__(self, master)
        self.images = {}
        self.height, self.width = height, width
        self.mine_count = mine_count 
        self.num_remaining = height * width
        self.tiles = []
        self.load_images(20)
        self.create_tiles()


    def load_images(self, tile_size):
        """Load tile images to be used in this game."""

        img_names = ["empty", "blank", "mine", "explode", "wrong", "flag"]
        img_names += ["number-%d" % i for i in range(1, 8)]
        for name in img_names:
            self.images[name] = PhotoImage(file="images/%s.gif" % name, 
                                           width=tile_size, height=tile_size)


    def create_tiles(self):
        """Create the grid of tiles, with dimensions self.height x 
        self.width. 

        """
        # Create blank tiles.
        for r in range(0, self.height):
            for c in range(0, self.width):
                tile = Button(self, image=self.images["blank"])
                tile.bind("<Button-1>", self.handle_left_click)
                tile.bind("<Button-3>", self.handle_right_click)
                tile.grid(row=r, column=c)
                tile.row, tile.column = r, c
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

            # Mine tiles have a value of -1.
            tile.value = -1
            num_mines -= 1

            # Update values of neighboring tiles.
            for n in self.find_neighbors(tile.row, tile.column):
                if not self.is_mine(n): 
                    n.value += 1
             

    def handle_left_click(self, event):
        """Uncover clicked tile."""

        self.reveal(event.widget)

        if self.check_win():
            self.win_game()


    def handle_right_click(self, event):
        """Mark tile with a flag if previously blank, unflag otherwise."""

        tile = event.widget
        tile["image"] = self.images["blank"] if tile.flag else self.images["flag"]
        tile.flag = not tile.flag


    def handle_double_click(self, event):
        """Uncover all neighboring non-mine tiles."""

        tile = event.widget
        neighbors = self.find_neighbors(tile.row, tile.column)

        # Check if tile value equals number of flagged neighbors.
        num_flags = sum([1 for n in neighbors if n.blank and n.flag])
        if num_flags != tile.value:
            return

        # Check if this move explodes any neighboring mines.
        mines, not_mines = [], []
        for n in neighbors:
            if not n.blank:
                continue
            if self.is_mine(n) and not n.flag: 
                # Neighboring mine not correctly identified.
                mines.append(n)
            elif not self.is_mine(n) and n.flag:
                # Neighboring tile wrongly identified as mine.
                not_mines.append(n)
    
        if len(mines) > 0 and len(not_mines) > 0:
            self.lose_game(mines, not_mines)
            return

        # Uncover all neighboring tiles that are not flagged.
        for p in self.find_neighbor_positions(tile.row, tile.column):
            n = self.tiles[p]
            if n.blank and not n.flag:
                self.reveal(n)

        if self.check_win():
            self.win_game()


    def reveal(self, tile):
        """Reveal contents of TILE."""

        self.num_remaining -= 1

        # If a mine tile, player loses.
        if self.is_mine(tile):
            self.lose_game([tile], [])
            return

        # If a numbered tile, uncover this tile only.
        if tile.value > 0:
            self.change_tile(tile, self.images["number-%d" % tile.value])
            return

        # This is an empty tile. 
        self.change_tile(tile, self.images["empty"])

        # Uncover neighboring blank tiles.
        for p in self.find_neighbor_positions(tile.row, tile.column):
            n = self.tiles[p]
            if n.blank:
                self.reveal(n)


    def change_tile(self, tile, img):
        """Change TILE to display new image IMG."""

        tile["state"] = DISABLED
        r, c = tile.row, tile.column
        tile.unbind("<Button-1>")
        tile.unbind("<Button-3>")
        new_tile = Label(self, image=img)
        new_tile.row, new_tile.column = r, c
        new_tile.blank = False
        new_tile.grid(row=r, column=c)
        new_tile["relief"] = SUNKEN
        if 0 < tile.value:
            new_tile.bind("<Double-Button-1>", self.handle_double_click)
            new_tile.value = tile.value
        self.tiles[self.width*r+c] = new_tile
       

    def check_win(self):
        """Check if the game has been won. This will be the case when the
        number of blank tiles is equal to the number of mines. 

        """
        return self.num_remaining <= self.mine_count


    def win_game(self):
        """Flag all mine tiles, if the player has not done so already.

        """
        for tile in self.tiles:
            if self.is_mine(tile):
                self.change_tile(tile, self.images["flag"])


    def lose_game(self, mines, not_mines):
        """Reveal the location of all mines."""

        for tile in self.tiles:
            if self.is_mine(tile):
                self.change_tile(tile, self.images["mine"])
            elif tile.blank:
                self.change_tile(tile, self.images["blank"])

        for mine in mines:
            self.change_tile(mine, self.images["explode"])

        for not_mine in not_mines:
            self.change_tile(not_mine, self.images["wrong"])


    def find_neighbors(self, r, c):
        """Return neighboring tiles of tile at row r and column c"""

        nbr_positions = self.find_neighbor_positions(r, c)
        return [self.tiles[p] for p in nbr_positions]


    def find_neighbor_positions(self, r, c):
        """Return positions of tiles neighboring tile at row r and column c."""

        nbr_coord = [ [r-1, c-1], [r-1, c], [r-1, c+1], [r, c+1], \
                      [r+1, c+1], [r+1, c], [r+1, c-1], [r, c-1]  ]  

        nbr_positions = []
        for r,c in nbr_coord:
            # Check if r and c are within table boundaries.
            if r >= 0 and r < self.height and c >= 0 and c < self.width: 
                nbr_positions.append(self.width*r+c)

        return nbr_positions
 

    def is_mine(self, tile):
        """True if TILE is a mine, false otherwise."""

        return tile.blank and tile.value == -1



####################################################
#                   Global Methods                 #
####################################################

def play(height, width, num_mines):
    """Start a new game with the specified height, width, and number of mines."""

    global app
    app.destroy()
    app = Application(height, width, num_mines, root)
    app.pack(side=BOTTOM)
    app.mainloop()


def play_easy():
    """Start a new game with a 9 x 9 tile grid and 10 mines."""

    play(9, 9, 10)


def play_medium():
    """Start a new game with a 16 x 16 tile grid and 40 mines."""

    play(16, 16, 40)


def play_difficult():
    """Start a new game with a 16 x 30 tile grid, and 99 mines."""

    play(16, 30, 99)



####################################################
#               Initializing the GUI               #
####################################################

root = Tk()
root.title('Minesweeper')

#Create menu.
menubar = Menu(root)

filemenu = Menu(menubar, tearoff=0)
filemenu.add_command(label="Exit", command=lambda: root.destroy())
menubar.add_cascade(label="File", menu=filemenu)
root.config(menu=menubar)

playmenu = Menu(menubar, tearoff=0)
playmenu.add_command(label="Easy", command=play_easy)
playmenu.add_command(label="Medium", command=play_medium)
playmenu.add_command(label="Difficult", command=play_difficult)
menubar.add_cascade(label="Play", menu=playmenu)
root.config(menu=menubar)

# Start game on default level "easy".
app = Application(9, 9, 10, root)
app.pack(side=BOTTOM)
app.mainloop()
root.mainloop()
