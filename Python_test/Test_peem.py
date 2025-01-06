import random

def deposit():
    amount = float(input("Enter your deposit $:"))
    if amount < 0:
        print("There not valid amount")
        return 0
    else:
        return amount


def play():
    global balance
    print(f"Your balance is: ${balance}")
    print("Hello everybody Let's play a game !!!!")
    print("Symbols: 🍇🍉🍊🍋🍎🍏🍐🥭")
    try:

        bet = int(input("Place your bet amount: "))

        if bet > balance:
            print("Your balance is not have")
        elif bet < 0:
            print("Your invalid amount")
        else:
            balance -= bet
            row = spin_row()
            print(f"Spinning....")
            print_row(row)
            payout = get_payout(row, bet)
            if payout > 0:
                print(f"Congratulations!! You win This round: ${payout}")
                play_again()
            else:
                print("Sorry You LOST!! This round")
                return play()
            balance += payout





    except ValueError:
        print("Invalid input!! Please enter a valid Number")
        return play()


def spin_row():
    symbols = ['🍇', '🍉', '🍊', '🍋', '🍎', '🍏', '🍐', '🥭']

    return [random.choice(symbols) for symbol in range(3)]


def print_row(row):
    print(" | ".join(row))


def play_again():
    choice = input("Do you want to play again?? (Y/N): ")
    if choice.upper() == "Y":
        return play()
    elif choice.upper == "N":
        return 0
    else:
        print("Your choice invalid !!!!")
        return play_again()


def get_payout(row, bet):
    if row[0] == row[1] == row[2]:
        if row[0] == "🍇":
            return bet * 2
        if row[0] == "🍉":
            return bet * 3
        if row[0] == "🍊":
            return bet * 5
        if row[0] == "🍋":
            return bet * 10
        if row[0] == "🍎":
            return bet * 20
        if row[0] == "🍏":
            return bet * 50
        if row[0] == "🍐":
            return bet * 100
        if row[0] == "🥭":
            return bet * 1000
    return 0


balance = 0
is_running = True

while is_running:
    print("*******************************")
    print(f"Your balance is: ${balance}")
    print("Welcome to Python SLOT MACHINE")
    print("1.Deposit balance")
    print("2.Play a game!!")
    print("*******************************")

    choice = input("Select your choice (1-2): ").upper()
    if choice == "1":
        balance += deposit()
    elif choice == "2":
        play()
    else:
        print("Your choice invalid")
