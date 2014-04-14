/**********************************************************************
 *  readme.txt template                                                   
 *  Kd-tree
**********************************************************************/

Name: James Evans
Login: jaevans
Precept: PO6A

Partner name: N/A     
Partner login: N/A 
Partner precept: N/A

/**********************************************************************
 *  Describe the Node data type you used to implement the
 *  2d-tree data structure.
 **********************************************************************/
 My Node data type includes four instance variables: a point (the
 2-D point which the Node represents), a rectangle (the portioned
 region of the 2D plane containing the point), and a left and right
 child. These nodes allow for a linked traversal of the KdTree, 
 in addition to quick access of the region containing the point
 for use in pruning and insertion methods. 

/**********************************************************************
 *  Describe your method for range search in a kd-tree.
 **********************************************************************/
 Range search operates according to a simple pruning heuristic. Points
 examined beginning at the root to determine whether they lie
 in the rectangle of interest. However, if a point's rectangle (i.e.
 the partitioned region containing that point) does not intersect
 the rectangle of interest, then that point is not considered and
 its subtree not searched. 


/**********************************************************************
 *  Describe your method for nearest neighbor search in a kd-tree.
 **********************************************************************/
 The heuristic for the nearest neighbor search is slightly more
 complicated, but nonetheless leads to effective run times in
 practical. The implementation of nearest neighbor search is
 recursive, beginning in the node and updating the "champion" (the
 point closest to the point of interest) after a closer distance is
 determined. However, if the shortest distance between the point
 of interest and a point's bounding box is greater than the distance
 between the point of interest and the champion, then that point
 is neglected and its subtree disregarded. To make better use of this
 pruning rule, the search method begins by traversing the tree as
 if the point of interest were being inserted into the kdtree (a
 pattern which generally leads to better champions earlier on 
 in the search). 


/**********************************************************************
 *  Give the total memory usage in bytes (using tilde notation and 
 *  the standard 64-bit memory cost model) of your 2d-tree data
 *  structure as a function of the number of points N. Justify your
 *  answer below.
 *
 *  Include the memory for all referenced objects (deep memory),
 *  including memory for the nodes, points, and rectangles.
 **********************************************************************/

bytes per Point2D: 32 bytes

bytes per RectHV: 48 bytes

bytes per KdTree of N points (using tilde notation):   ~112N
[include the memory for any referenced Node, Point2D and RectHV objects]


/**********************************************************************
 *  Give the expected running time in seconds (using tilde notation)
 *  to build a 2d-tree on N random points in the unit square.
 *  Justify your answer briefly with empirical evidence. (Do not
 *  count the time to generate the N points or to read them in
 *  from standard input.)
 **********************************************************************/
 Each insert operation is expected to require time proportional to
 lnN (as is generally the case with binary tree data structures). Since
 N of these operations will need to be performed to insert N points, 
 we expect 2d-tree construction to require NlogN time. 

 Below are the construction times for several input sizes (all files
 were constructed using the generator class):

 50k - 0.065
 100k - 0.082
 200k - 0.191
 400k - 0.386
 800k - 0.787
 1.6m - 1.694

 We see that as the input size is doubled, the time required increases
 by a factor slightly greater than two, as we might expect. Were the
 running time represented by a power law, we would have

 			T(N) = 2.89*10^(-7) * N^(1.09),

 validating our linearithmic hypothesis. 

/**********************************************************************
 *  How many nearest neighbor calculations can your brute-force
 *  implementation perform per second for input100K.txt (100,000 points)
 *  and input1M.txt (1 million points), where the query points are
 *  random points in the unit square? Explain how you determined the
 *  operations per second. (Do not count the time to read in the points
 *  or to build the 2d-tree.)
 *
 *  Repeat the question but with the 2d-tree implementation.
 **********************************************************************/

                     calls to nearest() per second
                     brute force           2d-tree
input100K.txt        1223		   746268
input1M.txt          10			   20000

To perform this calculation, I created a short test client which
created one KdTree and one PointSET object and filled these structures
with points from input of the desired size. Next, I employed the
Generator class to create a sample of 1000 random points in the unit
square; a Point2D is then created to contain these points. Finally, 
stopwatch objects are used to time the execution of "nearest"
calls on this array for both the kdtree and brute. The equation

	Calls per second = 1000/elapsed time

was used to determine the above values. 

/**********************************************************************
 *  Known bugs / limitations.
 **********************************************************************/
 No known bugs!

/**********************************************************************
 *  Describe whatever help (if any) that you received.
 *  Don't include readings, lectures, and precepts, but do
 *  include any help from people (including course staff, lab TAs,
 *  classmates, and friends) and attribute them by name.
 **********************************************************************/
 No help!

/**********************************************************************
 *  Describe any serious problems you encountered.                    
 **********************************************************************/
 Recursion generally takes me a while to wrap my around in the best
 of circumstances, so I initially had some difficulties with the
 private, recursive methods needed to implement the specified API. 
 At first, I found myself running into infinite loops where base 
 cases were unspecified, but after cracking the first such method
 (insertion), the pattern of searching downwards and then recursively
 passing objects back up the tree became more intuitive and easier
 to implement.    


/**********************************************************************
 *  If you worked with a partner, assert below that you followed
 *  the protocol as described on the assignment page. Give one
 *  sentence explaining what each of you contributed.
 **********************************************************************/
 N/A

/**********************************************************************
 *  List any other comments here. Feel free to provide any feedback   
 *  on how much you learned from doing the assignment, and whether    
 *  you enjoyed doing it.                                             
 **********************************************************************/
 I felt that KdTree was a very useful assignment, given the
 subtlety needed to implement the recursive methods for this
 rather intricate data structure. However, being able to think
 recursively is a pivotal skill in any programming environment, and
 this assignment certainly increased my comfort level with this style
 of programming. Moreover, it was quite a satisfying experience to
 observe the performance improvements realized through effective
 heuristic and pruning rule implementation. The combination of 
 clever algorithms with practical improvements is a powerful one, 
 and the design of a KdTree made that message all the more
 memorable. 




