import sys
import numpy as np
import random, math

if (len(sys.argv) < 6):
  print("Usage: python3 "  + sys.argv[0] + " population_size orgnization_size area avg_distance_between_atms iterations")
  sys.exit(1)
assert(len(sys.argv) == 6)

POP_SIZE = int(sys.argv[1])
ORG_SIZE = int(sys.argv[2])
AREA = float(sys.argv[3])
AREA_WIDTH = round(math.sqrt(AREA), 2)
AREA_HEIGHT = round(math.sqrt(AREA), 2)
AVG_DISTANCE_BETWEEN_ATMS = float(sys.argv[4])
ITERATIONS = int(sys.argv[5])

STRONG_TIE_PROBABILITY = 1e-7
STRONG_TIE_SUCCESS_RATE = 0.678
WEAK_TIE_SUCCESS_RATE = 0.400
NO_TIE_SUCCESS_RATE = 0.059

class User:
    def __init__(self, org, is_mutant):
        self.confidence = 50.0
        self.success_transactions = 0
        self.org = org
        # if a user is mutant, he will always "cheat" and cause the other party of transaction to loose confidence
        self.is_mutant = is_mutant
        pass
    def additive_decrease_confidence(self):
        if(self.confidence > 0):
            self.confidence -= 1
        else:
            self.confidence = 0
        pass
    def successful_transaction(self):
        self.success_transactions += 1
        pass
    def multiplicity_decrease_confidence(self):
        self.confidence /= 2
        pass
    def set_location(self, latitude, longitude):
        self.lat = latitude
        self.lon = longitude
        pass
    def get_location(self):
        return (self.lat, self.lon)
    def set_distance_to_requester(self, distance):
        self.distance_to_requester = distance
        pass
    def get_distance_to_requester(self):
        return self.distance_to_requester

def distance(u1, u2):
    return math.hypot(u2.lat - u1.lat, u2.lon - u1.lon)

def same_org(u1, u2):
    if u1.org is None or u2.org is None:
        return False
    elif u1.org == u2.org:
        return True
    else:
        return False
    pass


def transaction_accepted(requester, requestee):
    if(requestee.is_mutant):
        return True

    requestee_is_on_app = np.random.choice(2, 1, p=[1-requestee.confidence/100, requestee.confidence/100])[0]
    if not requestee_is_on_app:
        print('requestee not using app')
        return False


    are_friends = np.random.choice(2, 1, p=[1-STRONG_TIE_PROBABILITY, STRONG_TIE_PROBABILITY])[0]
    if are_friends:
        print('requestee is a friend')
        return np.random.choice(2, 1, p=[1-STRONG_TIE_SUCCESS_RATE, STRONG_TIE_SUCCESS_RATE])[0]

    if same_org(requester, requestee):
        print('requestee is in my org')
        agree_rate = (WEAK_TIE_SUCCESS_RATE * 100 + requester.success_transactions + requestee.success_transactions)/100.0
        return np.random.choice(2, 1, p=[1-agree_rate, agree_rate])[0]

    print('requestee is stranger')
    agree_rate = (NO_TIE_SUCCESS_RATE * 100 + requester.success_transactions + requestee.success_transactions)/100.0
    return np.random.choice(2, 1, p=[1-agree_rate, agree_rate])[0]
    pass


def assignLocations(requester):
    users_in_range = []
    # give all users random locations
    for j in range(0, POP_SIZE):
        if all_users[j] == requester:
            continue
        user_latitude = random.uniform(0, AREA_WIDTH)
        user_longitude = random.uniform(0, AREA_HEIGHT)
        all_users[j].set_location(user_latitude, user_longitude)
        if(distance(all_users[j], requester) < AVG_DISTANCE_BETWEEN_ATMS):
            # if user is within the distance add that user to a list
            all_users[j].set_distance_to_requester(distance(all_users[j], requester))
            users_in_range.append(all_users[j])
    return users_in_range



# Create users
all_users = []
for i in range(0, POP_SIZE):
    org = None
    if i < ORG_SIZE:
        org = 'ORG A'
    new_user = User(org, False)
    all_users.append(new_user)


results = []
for i in range(0, ITERATIONS):
    requester = all_users[random.randint(0, POP_SIZE-1)]
    percentage_confidence = requester.confidence/100
    if percentage_confidence > 1:
        # if over 100%, just use 100%
        percentage_confidence = 1

    usage = np.random.choice(2, 1, p=[1-percentage_confidence, percentage_confidence])
    if not usage:
        print('Requester chose not to use the app')
        # User has low confidence and chooses not to use cashme
        results.append(False)
        continue

    # generate a random location for the requester
    request_latitude = random.uniform(0, AREA_WIDTH)
    request_longitude = random.uniform(0, AREA_HEIGHT)
    requester.set_location(request_latitude, request_longitude)
    users_in_range = assignLocations(requester)
    users_in_range.sort(key=lambda x: x.distance_to_requester)

    performed = False
    for cur_user in users_in_range:
        perform_exchange = transaction_accepted(requester, cur_user)

        if(perform_exchange):
            if(cur_user.is_mutant and requester.is_mutant):
                print('both are mutants')
                cur_user.success_transaction = 0
                requester.success_transaction = 0
            elif(cur_user.is_mutant):
                print('requestee is mutant')
                cur_user.success_transaction = 0
                requester.multiplicity_decrease_confidence()
            elif(requester.is_mutant):
                print('requester is mutant')
                requester.success_transaction = 0
                cur_user.multiplicity_decrease_confidence()
            else:
                print('everyone\'s happy')
                cur_user.success_transactions += 1
                requester.success_transactions += 1
            performed = True
            results.append(performed)
            break
        else:
            continue
    # endfor
    if not performed:
        print("transaction was not performed")
        requester.additive_decrease_confidence()
        results.append(performed)


counter = 0
for ele in results:
    if ele is True:
        counter += 1

print(counter)
print("Transaction go through rate: ", float(counter) / ITERATIONS)
