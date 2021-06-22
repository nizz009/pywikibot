## File Info:

### Basic Operations

#### base_ops.py
Contains the basic operations/resuable code for working with Wikipedia and Wikidata pages.

##### [Recti/Modi]fications:
1. Add methods to add coordinates and maps in Wikidata

#### search_patterns.py
Extracts information from the Wikipedia articles

#### prop_id.py
Extracts information from the Wikipedia articles

##### [Recti/Modi]fications:
1. Improvise searching of the infobox

### Categories

#### import_soccerway_id.py
Adds the missing soccerway ids in Wd whose Wp pages use the socceryway id template <br>
Follows the following layout:
1. No IDs - get their ID
2. With IDs - check authenticity
	1. Correct - add to Wd
	2. Incorrect - get their ID

##### [Recti/Modi]fications:
1. checkAuthenticity (checks the Id present in the Wikipedia article) 
	1. add more criteria for checks (profession, birth date, etc.)

#### import_wta_id.py
Adds the missing WTA ids in Wd whose Wp pages use the WTA id template <br>
Follows the same layout as that of soccerway id

##### [Recti/Modi]fications:
1. difficulty in accessing the official site - SSL certificate error

#### import_atp_id.py
Adds the missing ATP ids in Wd whose Wp pages use the ATP id template <br>
Part of submissions during the contribution period

##### [Recti/Modi]fications:
1. Improvise the overall code

### Lists

#### nobel_laureates_phy.py

#### list_folk_heroes.py

#### historicplaces_riverhead_ny.py

## Things to work on:

1. Categories
2. Lists
3. Templates