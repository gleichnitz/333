public class BaseballElimination {
    private String[] teams; // String array to store names of teams
    private int[] w, l, r; // arrays to store wins, losses, and remaining games
    private int[][] g; // stores remaining games between two teams in 2D array
    private int n; // stores number of teams
    
    // hash table to store team names and their array index value
    private LinearProbingHashST<String, Integer> teamIds;
    
    private boolean[] isEliminated; // stores true for eliminated teams
    private SET<String>[] certificateOfElimination; // stores who eliminated who
    
    // create a baseball division from given filename in format specified below
    public BaseballElimination(String filename) {
        teamIds = new LinearProbingHashST<String, Integer>();
        
        // reading in files and constructing arrays
        In in = new In(filename);
        n = in.readInt();
        isEliminated = new boolean[n];
        certificateOfElimination = new SET[n];
        teams = new String[n];
        w = new int[n];
        l = new int[n];
        r = new int[n];
        g = new int[n][n];
        for (int i = 0; i < n; i++) {
            teams[i] = in.readString();
            teamIds.put(teams[i], i);
            w[i] = in.readInt();
            l[i] = in.readInt();
            r[i] = in.readInt();
            for (int j = 0; j < n; j++) {
                g[i][j] = in.readInt();
            }
        }
        
        // check whether each team is eliminated by creating flow networks
        for (int i = 0; i < n; i++) {
            checkElimination(i);
        }

    }
    
    // number of teams
    public int numberOfTeams() {                   
        return n;
    }
    
    // returns keys of items in hash table
    public Iterable<String> teams() {
        return teamIds.keys();
    }
    
    // number of wins for given team, exception if invalid team
    public int wins(String team) {
        if (teamIds.get(team) == null) 
            throw new java.lang.IllegalArgumentException();
        return w[teamIds.get(team)];
    }
    
    // number of losses for given team, exception if invalid team
    public int losses(String team) {
        if (teamIds.get(team) == null) 
            throw new java.lang.IllegalArgumentException();
        return l[teamIds.get(team)];
    }
    
    // number of remaining games for given team, exception if invalid team
    public int remaining(String team) {
        if (teamIds.get(team) == null) 
            throw new java.lang.IllegalArgumentException();
        return r[teamIds.get(team)];
    }
    
    // number of remaining games between team1 and team2`
    public int against(String team1, String team2) {
        if (teamIds.get(team1) == null) 
            throw new java.lang.IllegalArgumentException();
        if (teamIds.get(team2) == null) 
            throw new java.lang.IllegalArgumentException();
        return g[teamIds.get(team1)][teamIds.get(team2)];
    }
    
    /* private method which checks whether a given team is mathematically 
     * eliminated, and by whom
     */
    private void checkElimination(int t) {
        // number of total possible wins by team t
        int totalPossible = w[t] + r[t];
        
        // checks for trivial elimination
        for (int i = 0; i < n; i++) {
            if (totalPossible < w[i]) {
                isEliminated[t] = true;
                certificateOfElimination[t] = new SET<String>();
                certificateOfElimination[t].add(teams[i]);
                return;
            }
        }
        // number of team-team pair vertices
        int numGamesVertices = (n-1)*(n-2)/2;
        
        // number of vertices total
        int V = 1 + numGamesVertices + (n-1) + 1;
        
        // flow network for team t
        FlowNetwork flow = new FlowNetwork(V);
        
        // current vertex index
        int i = 1;
        
        // tracks total flow from the source (also, the number of games left)
        int totalGames = 0;
        
        // for each team-team pair vertex:
        for (int a = 0; a < n - 1; a++) {
            for (int b = a + 1; b < n - 1; b++) {
                
                // adjusts a and b so they accurately match array indices
                int teamIndex = t <= a ? a + 1 : a;
                int teamIndex2 = t <= b ? b + 1 : b;
                
                // connect source to team-team pair
                flow.addEdge(new FlowEdge(0, i, g[teamIndex][teamIndex2]));
                totalGames += g[teamIndex][teamIndex2];
                
                // connect team-team pair to both teams
                flow.addEdge(new FlowEdge(i, numGamesVertices + 1 + a, 
                                          Integer.MAX_VALUE));
                flow.addEdge(new FlowEdge(i, numGamesVertices + 1 + b,
                                          Integer.MAX_VALUE));
                i++;
            }
        }
        
        // connect each team to sink
        for (int j = 0; j < n - 1; j++) {
            int teamIndex = t <= j ? j + 1 : j;
            flow.addEdge(new FlowEdge(j + numGamesVertices + 1, V-1, 
                                      totalPossible - w[teamIndex]));
        }
        
        // if all edges pointing from sink are not, team is  eliminated
        FordFulkerson ford = new FordFulkerson(flow, 0, V-1);
        if (ford.value() < totalGames) {
            isEliminated[t] = true;  
            certificateOfElimination[t] = new SET<String>();
            // team eliminated by teams not in minimum cut
            for (int k = 0; k < n - 1; k++) {
                if (ford.inCut(1 + numGamesVertices + k)) {
                    int teamIndex = t <= k ? k + 1 : k;
                    certificateOfElimination[t].add(teams[teamIndex]);
                }
            }
            return;
        }
        isEliminated[t] = false;
    }
    
    /* retrieves whether the given team is eliminated
     * exception if invalid team
     */
    public boolean isEliminated(String team) {
        if (teamIds.get(team) == null) 
            throw new java.lang.IllegalArgumentException();
        int t = teamIds.get(team);
        return isEliminated[t];
    }
    
    /* retrieves the subset R of teams that eliminates given team
     * null if not eliminated, exception if invalid team
     */
    public Iterable<String> certificateOfElimination(String team) {
        if (teamIds.get(team) == null) 
            throw new java.lang.IllegalArgumentException();
        return certificateOfElimination[teamIds.get(team)];
    }
    
    public static void main(String[] args) {
        BaseballElimination division = new BaseballElimination(args[0]);
        for (String team : division.teams()) {
            if (division.isEliminated(team)) {
                StdOut.print(team + " is eliminated by the subset R = { ");
                for (String t : division.certificateOfElimination(team))
                    StdOut.print(t + " ");
                StdOut.println("}");
            }
            else {
                StdOut.println(team + " is not eliminated");
            }
        }
    }
}
