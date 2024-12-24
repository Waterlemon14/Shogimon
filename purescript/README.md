# cs150241project-lib

Kindly refer to [https://github.com/UPD-CS150-241/purescript-client-demo/](https://github.com/UPD-CS150-241/purescript-client-demo/) for sample code on how the modules in this package can be used.


# Issues:
- Getting clicked location
	- when board size > window size and scrolling down, mouse click does not get piece as dimension shizz


# Purescript Updates:
- Segmented into files for readability
- added isProtected in Piece
- increased board size to 8x8
- added 2 protected and 1 not protected pieces kinds
- protected cannot eat or be eaten


# Guides:
- Adding new piece *Kind*:
	1. ProjectTypes
		- | newKind in data Kind
		- show newKind in instance Show Kind
	2. Movements
		- add instance of getPossibleMoves for newKind
	3. Main 
		- add createNewKind function