from Tkinter import *
import random


class Application(Frame):
    """The Frame displaying the grid of tiles."""

    def __init__(self, height, width, mine_count, master):
        """Create a HEIGHT x WIDTH grid of tiles with MINE_COUNT mines."""

        Frame.__init__(self, master)
        self.images = {}    # Stores the tile images used in this game.
        self.height, self.width = height, width     # Dimensions of grid.
        self.mine_count = mine_count    # Number of mines in grid.
        self.num_remaining = height * width     # Number of remaining blank tiles.
        self.tiles = []     # Stores tile widgets.
        self.load_images()
        self.create_tiles()


    def load_images(self):
        """Load tile images to be used in this game."""

        img_names = ["blank", "empty", "mine", "explode", "wrong", "flag"]
        img_names += ["number-%d" % i for i in range(1, 8)]
        for name in img_names:
            self.images[name] = PhotoImage(file="images/%s.gif" % name, 
                                           width=20, height=20)


    def create_tiles(self):
        """Create grid of blank, mine, and numbered tiles."""

        # Create blank tiles.
        for r in range(0, self.height):
            for c in range(0, self.width):
                tile = Button(self, image=self.images["blank"])
                tile.bind("<Button-1>", self.handle_left_click)
                tile.bind("<Button-3>", self.handle_right_click)
                tile.grid(row=r, column=c)  # Set tile's location in grid.
                tile.row, tile.column = r, c
                tile.is_blank = True    # True if tile has not been clicked/revealed.
                tile.is_mine = False    # True if tile is a mine.
                tile.is_flag = False    # True if tile has been flagged.
                tile.value = 0          # Number of neigboring mines.
                self.tiles.append(tile)

        # Randomly assign mines to tiles.
        num_mines = self.mine_count
        while num_mines > 0:
            tile = random.choice(self.tiles)
            if tile.is_mine: 
                continue

            tile.is_mine = True
            num_mines -= 1

            # Increment values of neighboring tiles.
            for n in self.find_neighbors(tile):
                n.value += 1


    def handle_left_click(self, event):
        """Uncover clicked tile."""

        self.reveal_tile(event.widget)
        if self.is_win():
            self.win_game()


    def handle_right_click(self, event):
        """Mark tile with a flag if previously blank, unflag otherwise."""

        tile = event.widget
        tile["image"] = self.images["blank"] if tile.is_flag else self.images["flag"]
        tile.is_flag = not tile.is_flag


    def handle_double_click(self, event):
        """Uncover all neighboring non-mine tiles."""

        tile = event.widget
        neighbors = self.find_neighbors(tile)

        # Check if tile value equals number of flagged neighbors.
        num_flags = sum([1 for n in neighbors if n.is_flag])
        if num_flags != tile.value:
            return

        # Check if this move explodes any neighboring mines.
        mines, not_mines = [], []
        for n in neighbors:
            if not n.is_blank:
                continue
            if n.is_mine and not n.is_flag: 
                mines.append(n)
            elif not n.is_mine and n.is_flag:
                not_mines.append(n)
    
        if len(mines) > 0 and len(not_mines) > 0:
            self.lose_game(mines, not_mines)
            return

        # Uncover all neighboring blank tiles that are not flagged.
        self.reveal_neighboring_tiles(tile)

        if self.is_win():
            self.win_game()


    def reveal_tile(self, tile):
        """Reveal contents of TILE."""

        self.num_remaining -= 1

        # If mine tile, player loses.
        if tile.is_mine:
            self.lose_game([tile], [])
            return

        # If numbered tile, uncover this tile only.
        if tile.value > 0:
            self.change_tile(tile, self.images["number-%d" % tile.value])
            return

        # Empty tile. Uncover neighboring blank tiles.
        self.change_tile(tile, self.images["empty"])
        self.reveal_neighboring_tiles(tile)


    def reveal_neighboring_tiles(self, tile):
        """Reveal contents of TILE's neighbors."""

        # Note that we iterate over neighboring tile positions instead of the 
        # tiles themselves, since a tile might have changed in a prior iteration.
        for p in self.find_neighbor_positions(tile):
            n = self.tiles[p]
            if n.is_blank and not n.is_flag:
                self.reveal_tile(n)


    def change_tile(self, old_tile, img):
        """Replace TILE with new tile displaying image IMG."""

        old_tile["state"] = DISABLED
        old_tile.unbind("<Button-1>")
        old_tile.unbind("<Button-3>")

        new_tile = Label(self, image=img)
        new_tile.row, new_tile.column = old_tile.row, old_tile.column
        new_tile.is_blank = False
        new_tile.is_mine = old_tile.is_mine
        new_tile.is_flag = False
        new_tile.value = old_tile.value
        new_tile.grid(row=new_tile.row, column=new_tile.column)
        new_tile["relief"] = SUNKEN
        if not new_tile.is_mine and new_tile.value > 0:
            new_tile.bind("<Double-Button-1>", self.handle_double_click)
        self.tiles[self.width*new_tile.row+new_tile.column] = new_tile
       

    def is_win(self):
        """Check if the game has been won."""

        return self.num_remaining <= self.mine_count


    def win_game(self):
        """Reveal the location of mines by flagging all mine tiles, if the 
        player has not done so already.
        
        """
        for tile in self.tiles:
            if tile.is_mine and not tile.is_flag:
                self.change_tile(tile, self.images["flag"])


    def lose_game(self, mines, not_mines):
        """Reveal the location of all mines. MINES is a list containing
        mines that were not correctly identified. NOT_MINES contains tiles
        that were incorrectly identified as mines.
        
        """
        for tile in self.tiles:
            if tile.is_mine:
                self.change_tile(tile, self.images["mine"])
            elif tile.is_blank:
                self.change_tile(tile, self.images["blank"])

        for mine in mines:
            self.change_tile(mine, self.images["explode"])

        for not_mine in not_mines:
            self.change_tile(not_mine, self.images["wrong"])


    def find_neighbors(self, tile):
        """Return TILE's neighboring tiles."""

        nbr_positions = self.find_neighbor_positions(tile)
        return [self.tiles[p] for p in nbr_positions]


    def find_neighbor_positions(self, tile):
        """Return positions of TILE's neighbors in self.tiles."""

        r, c = tile.row, tile.column
        nbr_coord = [ [r-1, c-1], [r-1, c], [r-1, c+1], [r, c+1],
                      [r+1, c+1], [r+1, c], [r+1, c-1], [r, c-1]  ]  

        nbr_positions = []
        for r,c in nbr_coord:
            # Check if row and column are within table boundaries.
            if 0 <= r and r < self.height and 0 <= c and c < self.width: 
                nbr_positions.append(self.width*r+c)

        return nbr_positions
 


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
