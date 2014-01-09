from Tkinter import *
import random


class Application(Frame):

    #Constructor for Application class.
    def __init__(self, width, height, mine_count, master):
        Frame.__init__(self, master)
        self.master = master
        self.width = width
        self.height = height
        self.mine_count = mine_count 
        self.numbers = [one, two, three, four, five, six, seven, eight]
        self.tiles = []
        self.mines = []
        self.create_tiles()
        self.create_tile_mines()
        self.create_tile_nums()


    #Creates the grid of tiles, with dimensions self.height x self.width. 
    def create_tiles(self):
        for i in range(0, self.height):
            for j in range(0, self.width):
                tile = Button(self, image=blank)
                tile.bind("<Button-1>", self.handle_left_click)
                tile.bind("<Button-3>", self.handle_right_click)
                tile.grid(row=i, column=j)
                tile.row = i
                tile.column = j
                tile.blank = True
                tile.flag = False
                tile.contents = 0
                self.tiles.append(tile)


    #Assigns mines to certain tiles on a random basis. Number of mines
    #determined by self.mine_count.
    def create_tile_mines(self):
        num_mines = self.mine_count
        while num_mines > 0:
            mine_tile = random.choice(self.tiles)
            if mine_tile.contents != 10: 
                mine_tile.contents = 10
                self.mines.append(mine_tile)
                num_mines -= 1
             

    #Determines the number of mines neighboring each tile. This number
    #is what will appear when the blank tile is uncovered (clicked). If a 
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
    def handle_left_click(self, event):
        self.filter(event.widget)
        if self.check_win():
            self.win_game()


    #Called when a tile is clicked with the right mouse button.
    #Determines which tile was selected from EVENT and marks that tile
    #with a flag if previously blank or blank if previously flagged.
    def handle_right_click(self, event):
        tile = event.widget
        if tile.flag == True:
            tile["image"] = blank
            tile.flag = False
        else:
            tile["image"] = flag 
            tile.flag = True


    #Called when player double-clicks a tile, which in this game serves
    #to uncover all neighboring non-mine squares at once if the player has 
    #in fact properly indentified and flagged all neighboring mines.
    def handle_double_click(self, event):
        tile = event.widget
        neighbors = self.find_neighbors(tile.row, tile.column)
        count_flags = 0
        for n in neighbors:
            if n.blank == True and n.flag == True:
                count_flags += 1

        #Double-click is a valid move
        if count_flags == tile.contents:
            lost = []
            for n in neighbors:
                position = self.convert(n.row, n.column)
                if n.contents == 10 and not n.flag:
                    lost.append(n)
                elif n.contents != 10 and n.blank and n.flag:
                    self.change_tile(n, wrong)
    
            if len(lost) > 0:
                self.lose_game(lost)
                return

            for n in neighbors:
                if n.blank and n.contents != 10:
                    self.filter(n)

        if self.check_win():
            self.win_game()


    #Determines how TILE should be dealt with based on its type (whether
    #it contains a mine, has no neighboring mines, or has at least one
    #mine).
    def filter(self, tile):
        r = tile.row
        c = tile.column

        #Tile contains a mine. (Here I'm designating mine tiles as having
        #tile.contents values of 10.)
        if tile.contents == 10:
            self.lose_game([tile])

        #Tile has no neighboring mines.
        elif tile.contents == 0:
            self.change_tile(tile, empty)
            tile["state"] = DISABLED
            neighbors = self.find_neighbors(r, c)
            for n in neighbors:
                if n.blank:
                    self.filter(n)

        #Tile has at least one neighboring mine.
        else:
            self.change_tile(tile, self.numbers[tile.contents - 1])
            tile["state"] = DISABLED


    #Changes TILE so that it now displays the provided image IMG. For  
    #example, this would be used to change a blank tile to a tile
    #displaying the number of neighboring mines.
    def change_tile(self, tile, img):
        r = tile.row
        c = tile.column
        new_tile = Label(self, image=img)
        new_tile.row = r
        new_tile.column = c
        new_tile.blank = False
        new_tile.grid(row=r, column=c)
        new_tile["relief"] = SUNKEN
        if tile.contents != 10:
            new_tile.bind("<Double-Button-1>", self.handle_double_click)
            new_tile.contents = tile.contents
        self.tiles[self.convert(r, c)] = new_tile


    #Returns all neighboring tiles to the one at position (r, c).
    def find_neighbors(self, r, c):
        neighbors = []

        n_coord = [ [r-1, c-1], [r-1, c], [r-1, c+1], [r, c+1], \
                    [r+1, c+1], [r+1, c], [r+1, c-1], [r, c-1]  ]  

        for r,c in n_coord:
            if r >= 0 and r < self.height and c >= 0 and c < self.width: 
                neighbors.append(self.tiles[self.convert(r, c)])

        return neighbors
        

    #Checks if the game has been won. This will be the case when the number
    #of blank tiles is equal to the number of mines. 
    def check_win(self):
        count = 0
        for tile in self.tiles:
            if tile.blank:
                count += 1
        return count <= self.mine_count


    #Called when the game is won. Flags all mine tiles (if the player had
    #not done so already) and renders all remainig blank tiles immutable
    #and non-interactive (unclickeable).
    def win_game(self):
        for i in range(0, len(self.tiles)):
            tile = self.tiles[i]
            if tile.blank and tile.contents == 10:
                self.change_tile(tile, flag)

    #Called when the game is lost. Reveals the location of all mines and
    #renders all remaining blank tiles immutable and non-interactive
    #(unclickeable).
    def lose_game(self, mine_tiles):
        for i in range(len(self.tiles)):
            tile = self.tiles[i]
            if tile.contents == 10:
                self.change_tile(tile, mine)
            elif tile.blank:
                self.change_tile(tile, blank)

        for i in range(len(mine_tiles)):
            self.change_tile(mine_tiles[i], explode)


    #Given the position (ROW, COL) of a tile in the grid, finds tile's 
    #corresponding position in self.tiles.
    def convert(self, row, col):
        return self.width*row+col



####################################################
#                   Global Methods                 #
####################################################

def exit():
    root.destroy()

def play_easy():
    global app
    app.destroy()
    app = Application(9, 9, 10, root)
    app.pack(side=BOTTOM)
    app.mainloop()


def play_medium():
    global app
    app.destroy()
    app = Application(16, 16, 40, root)
    app.pack(side=BOTTOM)
    app.mainloop()

def play_difficult():
    global app
    app.destroy()
    app = Application(30, 16, 99, root)
    app.pack(side=BOTTOM)
    app.mainloop()



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
one = PhotoImage(file="images/one.gif", width=20, height=20)
two = PhotoImage(file="images/two.gif", width=20, height=20)
three = PhotoImage(file="images/three.gif", width=20, height=20)
four = PhotoImage(file="images/four.gif", width=20, height=20)
five = PhotoImage(file="images/five.gif", width=20, height=20)
six = PhotoImage(file="images/six.gif", width=20, height=20)
seven = PhotoImage(file="images/seven.gif", width=20, height=20)
eight = PhotoImage(file="images/eight.gif", width=20, height=20)

app = Application(30, 16, 99, root)
app.pack(side=BOTTOM)
app.mainloop()
root.mainloop()
