/*
 * Name: Vinay Ayyala
 * Login: vayyala
 * Precept: P02C
 * 
 * Inputs three integers as command-line arguments (x,y,z). 
 * Outputs the three integers and their sum in the form of an equation.
 * 
 * Compilation: javac SumThree.java
 * Execution: java SumThree num0 num1 num2
 * 
 * > java SumThree 3 4 5
 * 3 + 4 + 5 = 12
 * 
 * Header is based off of the header from the NameAge.java program 
 * from www.princeton.edu/~cos126/
 */

public class SumThree {
    public static void main(String[] args) {
        int x=Integer.parseInt(args[0]);
        int y=Integer.parseInt(args[1]);
        int z=Integer.parseInt(args[2]);
        int sum=x+y+z;
        System.out.println(x+" + "+y+" + "+z+" = "+sum);
    }
}
