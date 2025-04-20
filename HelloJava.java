/**
 * A colorful, engaging first Java program designed for ADHD learners.
 * This program demonstrates:
 * - Basic syntax with visual elements
 * - Immediate feedback
 * - Small, achievable code segments
 */
public class HelloJava {
    public static void main(String[] args) {
        // Welcome message with visual separation
        printSeparator();
        System.out.println("\u001B[1m\u001B[36mWelcome to Java for ADHD Learners!\u001B[0m");
        printSeparator();
        
        // Demonstrate variables with immediate visual feedback
        String name = "Learner";  // Try changing this to your name!
        int energy = 8;           // On a scale of 1-10
        
        // Visual representation of energy level
        System.out.print("Your energy level: ");
        for (int i = 0; i < 10; i++) {
            if (i < energy) {
                System.out.print("\u001B[32m■\u001B[0m"); // Green block
            } else {
                System.out.print("\u001B[31m□\u001B[0m"); // Red outline
            }
        }
        System.out.println(" (" + energy + "/10)");
        
        // Interactive elements (simulated)
        System.out.println("\nChoose your learning path:");
        System.out.println("1. \u001B[33m★\u001B[0m Quick visual examples");
        System.out.println("2. \u001B[35m♫\u001B[0m Code with music integration");
        System.out.println("3. \u001B[36m⚡\u001B[0m Game-based challenges");
        
        // Reminder for breaks
        System.out.println("\n\u001B[1m\u001B[34mRemember:\u001B[0m Take a 5-minute break every 20 minutes of coding!");
        
        // End with a motivational message
        printSeparator();
        System.out.println("\u001B[1m\u001B[32mYou've completed your first Java program!\u001B[0m");
        System.out.println("Small steps consistently = Big progress over time");
        printSeparator();
    }
    
    // Helper method for visual separation
    private static void printSeparator() {
        System.out.println("\u001B[35m" + "=".repeat(50) + "\u001B[0m");
    }
}
