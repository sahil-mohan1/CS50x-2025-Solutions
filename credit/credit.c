#include <cs50.h>
#include <stdio.h>

int main()
{
    // Declare variables
    long long number, card_no;
    int sum_2 = 0, sum_1 = 0, sum = 0, sum_2_temp = 0, no_of_digits = 0, valid = 0;
    // Prompt the user to enter a credit card number repeatedly until a positive number is entered
    do
        card_no = get_long_long("Enter card number: ");
    while (card_no <= 0);

    number = card_no;
    // Luhn's algorithm
    while (number > 0)
    {
        sum_1 += number % 10; // From right to left, digits at odd places are added to sum_1
        number /= 10;
        no_of_digits++;

        if (number > 0)
        {
            sum_2_temp = 0;
            sum_2_temp += 2 * (number % 10); // Digits at even places are multiplied by 2
            // If the product is a two digit number, the digits are added to sum_2
            if (sum_2_temp > 9)
                sum_2 += (sum_2_temp % 10 + sum_2_temp / 10);
            else
                sum_2 += sum_2_temp; // Else the product is directly added to sum_2
            number /= 10;
            no_of_digits++;
        }
    }

    sum = sum_1 + sum_2;

    if (sum % 10 == 0)
    {
        // Get first two digits
        long long first_two_digits = card_no;
        while (first_two_digits > 99)
            first_two_digits /= 10;
        // Determine card type and print result
        if ((first_two_digits == 34 || first_two_digits == 37) && no_of_digits == 15)
            printf("AMEX\n");
        else if (first_two_digits > 50 && first_two_digits < 56 && no_of_digits == 16)
            printf("MASTERCARD\n");
        else if ((first_two_digits > 39 && first_two_digits < 50) &&
                 (no_of_digits == 13 || no_of_digits == 16))
            printf("VISA\n");
        else
            printf("INVALID\n");
    }
    else
        printf("INVALID\n");
}
