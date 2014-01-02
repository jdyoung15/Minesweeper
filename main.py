from Tkinter import *
import random


class Application(Frame):

    def __init__(self, width, height, difficulty, master=None):
        Frame.__init__(self, master)
        self.master = master
        self.width = width
        self.height = height
        self.difficulty = difficulty
        self.numbers = [one, two, three, four, five, six, seven, eight]
        self.tiles = []
        self.mines = []
        self.create_tile_mines()
        self.create_tile_nums()


    #Called at the initialization of the grid of tiles. Designates certain 
    #tiles as containing mines on a random basis, with self.difficulty
    #acting as the (rough) probability that a tile will contain a mine.
    def create_tile_mines(self):
        for i in range(0, self.height):
            for j in range(0, self.width):
                button = Button(self, image=blank)
                button.bind("<Button-1>", self.handle_event)
                button.bind("<Button-3>", self.flag)
                button.grid(row=i, column=j)
                button.row = i
                button.column = j
                button.blank = True
                button.flag = False
                if random.random() < self.difficulty:
                    button.contents = 10 
                    self.mines.append(button)
                else:
                    button.contents = 0
                self.tiles.append(button)


    #Determines the number of mines neighboring each tile. This number
    #is what will appear if the blank tile is uncovered (clicked). If a 
    #tile has no neighboring mines, the uncovered tile will simply be blank.
    def create_tile_nums(self):
        for tile in self.tiles:
            if tile.contents != 10:
                count_mines = 0
                neighbors = self.find_neighbors(tile.row, tile.column)
                for n in neighbors:
                    if n.contents == 10:
                        count_mines += 1
                tile.contents = count_mines


    #Called when a tile is clicked with the left mouse button. The tile
    #in question is event.widget and is passed on to self.filter.
    def handle_event(self, event):
        self.filter(event.widget)


    #Called when a tile is clicked with the right mouse button.
    #Determines which tile was selected from EVENT and marks that tile
    #with a flag if previously blank or blank if previously flagged.
    def flag(self, event):
        tile = event.widget
        if tile.flag == True:
            tile["image"] = blank
            tile.flag = False
        else:
            tile["image"] = flag 
            tile.flag = True


    #Determines how TILE should be dealt with based on its type (whether
    #it's contains a mine, has no neighboring mines, or has at least one
    #mine).
    def filter(self, tile):
        r = tile.row
        c = tile.column

        #Tile contains a mine. (I'm designate mine tiles as having
        #tile.contents values of 10 here.)
        if tile.contents == 10:
            self.lose_game()
            self.tiles[self.convert(r, c)] = self.change_tile(tile, explode)
            self.clean_up()

        #Tile has no neighboring mines.
        elif tile.contents == 0:
            new = self.change_tile(tile, empty)
            self.tiles[self.convert(r, c)] = new
            tile["state"] = DISABLED
            neighbors = self.find_neighbors(r, c)
            for n in neighbors:
                if n.blank == True:
                    self.filter(n)

        #Tile has at least one neighboring mine.
        else:
            new = self.change_tile(tile, self.numbers[tile.contents - 1])
            self.tiles[self.convert(r, c)] = new
            tile["state"] = DISABLED


    #Changes the tile image when tile is clicked. I.e. transforms a blank
    #tile into a tile that display a number indicating the number of 
    #neighboring mines.
    def change_tile(self, tile, img):
        r = tile.row
        c = tile.column
        new = Label(self, image=img)
        new.row = r
        new.column = c
        new.blank = False
        new.grid(row=r, column=c)
        new["relief"] = SUNKEN
        if tile.contents != 10:
            new.bind("<Double-Button-1>", self.double)
            new.contents = tile.contents
        return new


    #Called when player double-clicks a tile, which in this game serves
    #to uncover all neighboring non-mine squares at once if the player has 
    #in fact properly indentified and flagged all neighboring mines.
    def double(self, event):
        tile = event.widget
        neighbors = self.find_neighbors(tile.row, tile.column)
        count_flags = 0
        for n in neighbors:
            if n.blank == True and n.flag == True:
                count_flags += 1
        if count_flags == tile.contents:
            self.uncover_double(tile.row, tile.column)


    #Uncovers all neighboring non-mine tiles following a double-click.
    #If it turns out that the player has flagged the wrong tiles, 
    #this method will uncover the real mine tile and end the game.
    def uncover_double(self, r, c):
        neighbors = self.find_neighbors(r, c)
        lost = False
        for n in neighbors:
            if n.blank == True:
                position = self.convert(n.row, n.column)
                if n.contents == 0:
                    self.tiles[position] = self.change_tile(n, empty)
                    self.filter(n)
                elif n.contents != 10 and n.flag == True:
                    self.tiles[position] = self.change_tile(n, wrong)
                elif n.contents != 10:
                    self.tiles[position] = self.change_tile(n, \
                        self.numbers[n.contents - 1])
                elif n.contents == 10 and n.flag == False:
                    self.tiles[position] = self.change_tile(n, explode)
                    lost = True

        if lost == True:
            self.lose_game()
            self.clean_up()


    #Returns all neighboring tiles to the one at position (r, c).
    def find_neighbors(self, r, c):
        neighbors = []
        n_coord = [ [r - 1, c - 1],     \
                    [r - 1, c],         \
                    [r - 1, c + 1],     \
                    [r, c + 1],         \
                    [r + 1, c + 1],     \
                    [r + 1, c],         \
                    [r + 1, c - 1],     \
                    [r, c - 1]          ]  

        for n in n_coord:
            if self.check(n[0], n[1]): 
                neighbors.append(self.tiles[self.convert(n[0], n[1])])

        return neighbors
        

    #Determines whether the provided coordinates ROW and COL are valid
    #positions in the grid.
    def check(self, row, col):
        return row >= 0 and row < self.height and col >= 0 \
            and col < self.width 


    #Given the position (ROW, COL) of a tile in the grid, finds tile's 
    #corresponding position in self.tiles.
    def convert(self, row, col):
        return self.width*row+col


    #Reveals the location of all mines when the game is lost.
    def lose_game(self):
        for i in range(0, len(self.mines)):
            self.change_tile(self.mines[i], mine) 
        

    #Transforms all non-mine tiles into permanent blank tiles, thus
    #preventing the player from uncovering them once the game is over.
    def clean_up(self):
        for i in range(0, len(self.tiles)):
            tile = self.tiles[i]
            if tile.blank == True and tile.contents != 10:
                new = Label(self, image=blank)
                new.grid(row=tile.row, column=tile.column)
                self.tiles[i] = new



root = Tk()

#Load images.
empty = PhotoImage(file="images/empty.gif", width=20, height=20)
blank = PhotoImage(file="images/blank.gif", width=20, height=20)
mine = PhotoImage(file="images/mine.gif", width=20, height=20)
explode = PhotoImage(file="images/explode.gif", width=20, height=20)
wrong = PhotoImage(file="images/wrong.gif", width=20, height=20)
flag = PhotoImage(file="images/flag.gif", width=20, height=20)
one = PhotoImage(file="images/one.gif", width=20, height=20)
two = PhotoImage(file="images/two.gif", width=20, height=20)
three = PhotoImage(file="images/three.gif", width=20, height=20)
four = PhotoImage(file="images/four.gif", width=20, height=20)
five = PhotoImage(file="images/five.gif", width=20, height=20)
six = PhotoImage(file="images/six.gif", width=20, height=20)
seven = PhotoImage(file="images/seven.gif", width=20, height=20)
eight = PhotoImage(file="images/eight.gif", width=20, height=20)

root.title('Minesweeper')
app = Application(30, 15, 0.10, master=root)
app.pack(side=BOTTOM)
app.mainloop()
root.destroy()
