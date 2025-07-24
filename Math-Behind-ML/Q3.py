def get_positive_int(prompt):
    while True:
        try:
            value = int(input(prompt))
            if value <= 0:
                print("Please enter a positive integer.")
                continue
            return value
        except ValueError:
            print("Invalid input. Please enter a positive integer.")

def get_non_negative_int(prompt):
    while True:
        try:
            value = int(input(prompt))
            if value < 0:
                print("Please enter a non-negative integer.")
                continue
            return value
        except ValueError:
            print("Invalid input. Please enter a non-negative integer.")

def main():
    total_emails = get_positive_int("Enter total number of emails: ")
    emails_with_free = get_non_negative_int("Enter number of emails containing 'free': ")
    spam_emails = get_non_negative_int("Enter number of spam emails: ")
    spam_and_free = get_non_negative_int("Enter number of emails that are both spam and contain 'free': ")

    # Validation
    if emails_with_free > total_emails:
        print("Number of emails with 'free' cannot exceed total emails.")
        return
    if spam_emails > total_emails:
        print("Number of spam emails cannot exceed total emails.")
        return
    if spam_and_free > spam_emails or spam_and_free > emails_with_free:
        print("Number of emails that are both spam and contain 'free' cannot exceed spam emails or emails with 'free'.")
        return
    if emails_with_free == 0:
        print("Cannot compute probability: no emails contain 'free'.")
        return
    if spam_emails == 0:
        print("Cannot compute probability: no spam emails.")
        return

    P_spam = spam_emails / total_emails
    P_free = emails_with_free / total_emails
    P_free_given_spam = spam_and_free / spam_emails

    P_spam_given_free = (P_free_given_spam * P_spam) / P_free

    print(f"P(Spam | Free) = {P_spam_given_free:.4f}")

if __name__ == "__main__":
    main()
