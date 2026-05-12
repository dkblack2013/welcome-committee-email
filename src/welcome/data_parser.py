"""
Data Parser and Sorter Agent
Parses email bodies to extract family details, aggregates data, and sorts into ministry buckets.
"""

import re
from typing import List, Dict, Any, Set
from collections import defaultdict

# Ministry buckets as per project specs
MINISTRY_BUCKETS = [
    "General Welcoming Email List",
    "Young Adult Ministry",
    "Bible Studies",
    "Family of Faith Formation",
    "Women's Fellowship",
    "Men's Guild",
    "RCIA",
    "Women's Group",
    "Respect Life",
    "Choir/Music Ministry",
    "Garden Crew",
    "SVDP",
    "Thanksgiving Dinner",
    "Worship Commission",
    "Adornment",
    "Building & Grounds",
    "Parish Council",
    "Lectors",
    "Eucharistic Minister",
    "Knights of Columbus",
    "Home Distributors of Holy Communion",
    "Bereavement",
    "Ushers",
    "Altar Servers",
    "EPIC",
    "Stewardship Commission",
    "Greeters",
    "Church Cleaning"
]

def parse_emails(emails: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """
    Parse email bodies to extract family details and sort into buckets.

    Args:
        emails: List of email dictionaries from fetcher.

    Returns:
        Dict with bucket names as keys, lists of family dicts as values.
    """
    all_families = []

    for email in emails:
        families = extract_families_from_body(email['body'])
        date_epoch = email.get('internal_date_epoch')
        for family in families:
            family['date_received_epoch'] = date_epoch
        all_families.extend(families)

    # print(f"Total families before aggregation: {len(all_families)}")  # Debug print

    # Aggregate and deduplicate
    aggregated_families = aggregate_families(all_families)

    # print(f"Total members after aggregation: {len(aggregated_families)}")  # Debug print

    # Sort into buckets
    bucketed_families = sort_into_buckets(aggregated_families)

    return bucketed_families

def extract_families_from_body(body: str) -> List[Dict[str, Any]]:
    """
    Extract family details from email body text based on generic pattern.

    Args:
        body: Plain text body of the email.

    Returns:
        List of family dictionaries (one per email), each with members and interests.
    """
    families = []
    lines = body.split('\n')
    current_family = {'members': [], 'interests': []}
    current_adult = {}
    adult_section = None

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Check for section headers
        if 'Adult 1' in line:
            if current_adult:
                current_family['members'].append(current_adult)
            current_adult = {'type': 'adult1'}
            adult_section = 'adult1'
            # print(f"Started Adult 1 section")  # Debug print
        elif 'Adult 2' in line:
            if current_adult:
                current_family['members'].append(current_adult)
            current_adult = {'type': 'adult2'}
            adult_section = 'adult2'
            # print(f"Started Adult 2 section")  # Debug print
        elif ':' in line:
            key, value = line.split(':', 1)
            key = key.strip('*').strip()  # Remove markdown * from key
            value = value.strip('*').strip()  # Remove markdown * from value
            # print(f"Parsed: {key} = {value}")  # Debug print

            if key == 'Family Last Name':
                current_family['family_name'] = value
            elif key == 'First Name' and adult_section:
                current_adult['first_name'] = value
                # print(f"Set first_name: {value}")  # Debug print
            elif key == 'Last Name' and adult_section:
                current_adult['last_name'] = value
                # print(f"Set last_name: {value}")  # Debug print
            elif key == 'Email' and adult_section:
                current_adult['email'] = value
                # print(f"Set email: {value}")  # Debug print
            elif 'getting involved with' in key:  # More flexible match for interests
                interests_str = value
                current_family['interests'] = [i.strip() for i in interests_str.split('|') if i.strip()]

    # Add last adult
    if current_adult:
        current_family['members'].append(current_adult)

    # Add family if it has members
    if current_family['members']:
        families.append(current_family)

    return families

def aggregate_families(families: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Aggregate and deduplicate families by email, flattening members.

    Args:
        families: List of family dicts with members.

    Returns:
        Deduplicated list of individual family members with interests.
    """
    member_map = {}

    for family in families:
        interests = family.get('interests', [])
        family_name = family.get('family_name', '')
        date_epoch = family.get('date_received_epoch')
        for member in family.get('members', []):
            email = member.get('email', '').lower()
            if not email:
                continue

            first_name = member.get('first_name', '')
            last_name = member.get('last_name', '')

            if email not in member_map:
                member_map[email] = {
                    'name': f"{first_name} {last_name}".strip(),
                    'first_name': first_name,
                    'last_name': last_name,
                    'family_name': family_name,
                    'email': email,
                    'interests': set(),
                    'date_received_epoch': date_epoch,
                }
            else:
                # Keep the earliest date_received we've seen for this person
                existing = member_map[email].get('date_received_epoch')
                if date_epoch is not None and (existing is None or date_epoch < existing):
                    member_map[email]['date_received_epoch'] = date_epoch

            member_map[email]['interests'].update(interests)

    # Convert sets back to lists
    for member in member_map.values():
        member['interests'] = list(member['interests'])

    return list(member_map.values())

def sort_into_buckets(members: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """
    Sort members into ministry buckets based on interests.

    Args:
        members: List of aggregated member dicts.

    Returns:
        Dict with bucket names as keys, member lists as values.
    """
    buckets = defaultdict(list)

    for member in members:
        interests = member.get('interests', [])
        assigned_buckets = set()

        bucket_lookup = {bucket.lower(): bucket for bucket in MINISTRY_BUCKETS}
        for interest in interests:
            canonical = bucket_lookup.get(interest.strip().lower())
            if canonical:
                assigned_buckets.add(canonical)

        # If no matches, assign to General
        if not assigned_buckets:
            assigned_buckets.add("General Welcoming Email List")

        # Add member to each assigned bucket
        for bucket in assigned_buckets:
            buckets[bucket].append(member)

    return dict(buckets)

# Validation: Test function
if __name__ == '__main__':
    # Load generic email pattern and create sample
    pattern_path = '../../planning/generic-email-pattern.md'
    try:
        with open(pattern_path, 'r') as f:
            pattern = f.read()
    except FileNotFoundError:
        print("Pattern file not found. Using hardcoded sample.")
        pattern = """
Family Information
Family Last Name: Doe

Adult 1
First Name: John
Last Name: Doe
Email: john@example.com

Adult 2
First Name: Jane
Last Name: Doe
Email: jane@example.com

Please select areas within our parish community that you may be interested in getting involved with.: Church Cleaning|Garden Crew
        """

    # Replace ### with sample data
    sample_data = [
        "Doe",  # Family Last Name
        "123 Main St",  # Street Address
        "",  # Street Address Line 2
        "Anytown",  # City
        "CA",  # State
        "12345",  # Zip
        "Previous Parish",  # Previous Parish
        "Married",  # Household Type
        "Tithing",  # Contribution Type
        "Yes",  # Children
        "2",  # Adults
        "John",  # Adult 1 First
        "Doe",  # Adult 1 Last
        "",  # Maiden
        "Male",  # Gender
        "john@example.com",  # Email
        "123-456-7890",  # Phone
        "01/01/1980",  # DOB
        "Married",  # Marital
        "01/01/2000",  # Marriage Date
        "St. Cecilia",  # Marriage Church
        "Jane",  # Adult 2 First
        "Doe",  # Adult 2 Last
        "",  # Maiden
        "Female",  # Gender
        "jane@example.com",  # Email
        "098-765-4321",  # Phone
        "01/01/1982",  # DOB
        "Married",  # Marital
        "01/01/2000",  # Marriage Date
        "St. Cecilia",  # Marriage Church
        "2",  # Children count
        "Church Cleaning|Garden Crew|Young Adult Ministry"  # Interests
    ]

    sample_body = pattern
    for data in sample_data:
        sample_body = sample_body.replace('###', data, 1)

    sample_emails = [{'body': sample_body}]
    result = parse_emails(sample_emails)
    print("Bucketed Families from Generic Pattern:")
    for bucket, families in result.items():
        print(f"{bucket}: {len(families)} families")
        for family in families:
            print(f"  - {family['name']} ({family['email']}) - Interests: {family['interests']}")