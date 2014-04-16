/*
 * Name: rfreling
 * Login: rfreling
 * Precept: P02C
 * 
 * Inputs four names as command-line arguments.
 * Outputs a sentence with the names in reverse of the order inputted. 
 * 
 * Compilation: javac HiFour.java
 * Execution: java HiFour name0 name1 name2 name3
 * 
 * > java HiFour Jacob Josh Justin John
 * Hi John, Justin, Josh, and Jacob.
 * 
 * Header is based off of the header from the NameAge.java program 
 * from www.princeton.edu/~cos126/
 */

public class HiFour {
    public static void main(String[] args) {
        System.out.print("Hi "+args[3]+", "+args[2]+", "
                             +args[1]+", and "+args[0]+".");
    }
}
