// My first program
public class SumThree {

    // Print out the sum of three command line integers. 
    public static void main(String[] args) {

        int x=Integer.parseInt(args[0]);
        int y=Integer.parseInt(args[1]);
        int z=Integer.parseInt(args[2]);

        int sum=x+y+z;

        System.out.println(x+" + "+y+" + "+z+" = "+sum);

    }
}
