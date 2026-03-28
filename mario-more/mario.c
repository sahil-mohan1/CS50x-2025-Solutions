#include <cs50.h>
#include <stdio.h>

int main()
{
    int i, j, height; // declare variables for loop and pyramid height
    // prompt the user for a height between 1 and 8 until valid input is given
    do
        height = get_int("Height: ");
    while (height < 1 || height > 8);

    for (i = 0; i < height; i++) // Outer loop controls height of the pyramids
    {
        for (j = 0; j < height - i - 1; j++) // prints left side spaces
            printf(" ");

        for (j = 0; j < i + 1; j++) // prints left sides hashes
            printf("#");

        printf("  "); // prints two spaces between the pyramids

        for (j = 0; j < i + 1; j++) // prints right sides hashes
            printf("#");

        printf("\n"); // move onto the next line
    }
}
