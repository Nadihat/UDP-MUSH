# Java Course for ADHD Learners

## Course Philosophy
This course is designed with ADHD-friendly learning strategies:
- Short, focused lessons (15-20 minutes)
- Visual aids and concrete examples
- Hands-on coding from day one
- Immediate feedback loops
- Gamified progression system
- Regular breaks built into the structure

## Course Structure

### Module 1: Java Fundamentals (The Exciting Stuff First!)
**Session 1: Your First Java Program (15 min)**
- Create and run a simple program that does something visually interesting
- Quick win: See your code work immediately
```java
public class ColorfulHello {
    public static void main(String[] args) {
        System.out.println("\u001B[31mRed\u001B[0m");
        System.out.println("\u001B[32mGreen\u001B[0m");
        System.out.println("\u001B[34mBlue\u001B[0m");
    }
}
```

**Session 2: Variables as Containers (15 min)**
- Visual metaphor: Variables as labeled boxes
- Hands-on: Create variables that store interesting information about yourself
```java
String myName = "Your Name";
int myAge = 25;
boolean likesJava = true;
System.out.println("Hi, I'm " + myName + "!");
```

**Session 3: Making Decisions with If/Else (20 min)**
- Real-world example: Program that gives different responses based on time of day
- Activity: Build a simple mood-based recommendation engine
```java
int currentHour = 15; // 3 PM
if (currentHour < 12) {
    System.out.println("Good morning! Time for coffee?");
} else if (currentHour < 18) {
    System.out.println("Good afternoon! Take a quick stretch break!");
} else {
    System.out.println("Good evening! How was your day?");
}
```

### Module 2: Loops and Arrays (Pattern Power)
**Session 1: Loops as Superpowers (15 min)**
- Visualize loops as automation tools
- Create visual patterns with loops
```java
// Create a triangle pattern
for (int i = 1; i <= 5; i++) {
    for (int j = 1; j <= i; j++) {
        System.out.print("* ");
    }
    System.out.println();
}
```

**Session 2: Arrays as Collections (20 min)**
- Visual metaphor: Arrays as organized shelves
- Build a simple playlist program
```java
String[] favoriteSongs = {"Song 1", "Song 2", "Song 3", "Song 4"};
System.out.println("My top " + favoriteSongs.length + " songs:");
for (int i = 0; i < favoriteSongs.length; i++) {
    System.out.println((i+1) + ". " + favoriteSongs[i]);
}
```

### Module 3: Methods and Objects (Building Blocks)
**Session 1: Methods as Recipes (15 min)**
- Methods as reusable recipes you can call anytime
- Create helper methods for common tasks
```java
public static void printWithBox(String message) {
    String border = "+";
    for (int i = 0; i < message.length() + 2; i++) {
        border += "-";
    }
    border += "+";
    
    System.out.println(border);
    System.out.println("| " + message + " |");
    System.out.println(border);
}

// Using it
printWithBox("Hello World");
printWithBox("Java is fun!");
```

**Session 2: Objects as Digital Pets (20 min)**
- Create a simple digital pet class
- Give it properties and behaviors
```java
class DigitalPet {
    String name;
    int happiness = 5;
    
    void feed() {
        happiness += 2;
        System.out.println(name + " says: Yum! Happiness: " + happiness);
    }
    
    void play() {
        happiness += 3;
        System.out.println(name + " jumps with joy! Happiness: " + happiness);
    }
}

// Using it
DigitalPet myPet = new DigitalPet();
myPet.name = "Pixel";
myPet.feed();
myPet.play();
```

## Learning Strategies

### Focus Techniques
- **Pomodoro Technique**: 15-20 minute coding sessions with 5 minute breaks
- **Body Doubling**: Join online coding sessions with others
- **Gamification**: Track streaks of daily coding practice

### Environment Setup
- Minimize distractions in your coding environment
- Use noise-cancelling headphones or background music if helpful
- Keep fidget tools nearby for restless energy

### Project-Based Learning
Each module culminates in a small, complete project:
1. Module 1 Project: Interactive Story Generator
2. Module 2 Project: Pattern-Based Art Generator
3. Module 3 Project: Virtual Pet Simulator

## Resources
- Visual cheat sheets for Java syntax
- Recommended IDE: IntelliJ IDEA (with distraction-free mode)
- Community Discord for accountability partners

## Next Steps
After completing this course, you'll have the foundation to:
1. Build simple Java applications
2. Understand core programming concepts
3. Move on to more advanced Java topics like inheritance, interfaces, and collections

Remember: Consistent small steps beat irregular large efforts. Celebrate each small win!
