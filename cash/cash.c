#include <cs50.h>
#include <stdio.h>

int main(void)
{
    int cents, quarters, dimes, nickels, pennies, sum;
    // Prompt the user for change owed, in cents
    do
    {
        cents = get_int("Change owed: ");
    }
    while (cents < 0);
    // Calculate the number of quarters, dimes, nickels, and pennies
    quarters = cents / 25;
    cents %= 25;
    dimes = cents / 10;
    cents %= 10;
    nickels = cents / 5;
    cents %= 5;
    pennies = cents;
    // Calculate the total number of coins
    sum = quarters + dimes + nickels + pennies;
    printf("%d\n", sum);
}
