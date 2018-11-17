user specs layout in DSL

DSL renders data structure of full layout in current state

that data structure given to diffing code which compares it to current state

side-effects triggered in UI to bring interface up to the new state.

state stored as new "current" state



We can map

id -> content
id -> UI element

id -> path
id -> container(?) since container will need to know of its coming and going



## reordering

let i be the index of lo, starting at 0
let n be the index of lo', starting at 0
let s be the set of of 'reorderd' widgets in this container (starting at the empty set)

consider

lo  [a b c d]
lo' [a c b d]

iterate each list in parallel

is lo[i] in the local reordered set? if so, advance lo (increment i)

is lo[i] == lo'[n]?
yes, advance both lists
no?
  - remove lo'[n] from UI (can be done with widget ID)
  - insert lo'[n] at index n in the UI (insertWidget takes an index)
  - store lo'[n] in "reordered" set locally
  - advance lo' (increment n)

consider

lo [a b c d]
lo' [a c d]

iterate each list in parallel
is lo[i] == lo'[n]?
yes, advance both lists
no?
    - is lo[i] in the dict of removed or moved elements?
    - if yes
        - remove the element from the UI
        - increment i (and not n) and move on

consider
lo  [a b c d]
lo' [a b e c d]

iterate each list in parallel
is lo[i] == lo'[n]?
yes, advance both lists
no?
    - is lo'[n] in the dict of added or moved elements?
    - if yes
        - insert element at index n
        - advance n (not i) and continue
