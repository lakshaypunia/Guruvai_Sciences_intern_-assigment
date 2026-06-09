# Solution Explanation

For the first question, I have used the combination of a hash map and a doubly linked list, as the hash map provides fast searching with $O(1)$ time complexity and we use the doubly linked list to update the elements' positions. The core logic is that whenever we use an item, we detach it from the list if it is already there and connect it to the head. This operation takes $O(1)$ time complexity in a doubly linked list. We do the same while adding a new element, and we remove the least used element—which is the previous one from the tail—when the size which we have determined gets full. Both these get and put operations complete in $O(1)$ time complexity.

For the second question, to solve both parts we have to sort the list first and then perform the operations. For checking if a person can attend all the meetings, we will iterate over the list and check if current.starttime < prev.endtime. If yes, then the person cannot attend all the meetings, and if no, he can attend all the meetings.

For part 2, we will use the sorted array and a min-heap. We will push the end time of the first meeting into the heap—basically assigning a room for it—then we process the second meeting and compare its start time with the end time of the top of the heap. This will tell us if the room is free at that time. If yes, we will replace the top element with the current element's end time. If no, we will add a new room to the min-heap.

For the final discussion:

- **LRU Cache (put & get):** The time complexity for both functions is $O(1)$ and the space complexity is $O(c)$, where $c$ is the cache capacity.

- **can_attend_all & min_room_required:** For both, the time complexity is $O(n \log n)$ as both functions include sorting whose time complexity is $O(n \log n)$. The min_room_required function also includes a min-heap which requires $O(n \log n)$ total time for operations, and this is the most dominant cost, so the time complexity for both functions is $O(n \log n)$. In both functions, the heap holds at most $n$ entries, so the space complexity is $O(n)$.

I have already answered the question of why we have used the combination of a hash map and a doubly linked list above. The hash map provides us with a searching speed of $O(1)$ and the doubly linked list provides us with deletion, insertion, and updation speeds of $O(1)$, completing our goal of getting $O(1)$ time complexity. (Note: You wrote "heap and doubly linked list" in your draft, which was changed to "hash map" to match your explanation).

I have also implemented the function to assign rooms. First, we take all the available rooms and we will have a list or a stack of free rooms. While storing the time slots in the min-heap, we store a tuple in it which contains the end time and room name. Whenever we replace that element from the heap, we will add that room name back to the free rooms list so that whenever a new room is needed, we can take a name from that list and use it there.

To make our implementation thread-safe, we have used threading.Lock to prevent race conditions and pointer corruption.
