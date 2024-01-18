class EventEntitiesTemplate:
    examples = [
        {
            "query": "Arrange a team-building picnic at a local park for our department next week",
            "answer": "{{\"Purpose of the event\": [\"Team-building picnic\"], "
                      "\"Deadline\": [\"Next week\"], "
                      "\"Preferred time\": [\"Morning\", \"Afternoon\", \"Evening\"], "
                      "\"Location\": [\"Local park\", \"Outdoor recreational area\", \"Nearby botanical garden\"], "
                      "\"Number of guests\": [\"20-30\", \"30-50\", \"More than 50\"], "
                      "\"Budget range\": [\"$500 - $1,000\", \"$1,000 - $1,500\", \",more than $1,500\"], "
                      "\"Specific themes or colors for decorations/styling\": [\"Casual and fun (Bright, playful colors)\", \"Nature-inspired (Greens and earth tones)\", \"Company branding (Company colors and logos)\"], "
                      "\"Entertainment/activities\": [\"Outdoor games (e.g., Frisbee, volleyball)\", \"Potluck-style lunch\", \"Music playlist\", \"Team-building exercises\", \"Relaxation zones (e.g., hammocks, picnic blankets)\"]}}"
        }, {
            "query": "Organize a birthday party for my son with a live-music band",
            "answer": "{{\"Purpose of the event\": [\"My son's birthday\"], "
                      "\"Deadline\": [\"One week\", \"2 weeks\", \"One month\"], "
                      "\"Preferred time\": [\"Morning\", \"Afternoon\", \"Evening\"], "
                      "\"Location\": [\"Home\", \"Restaurant\", \"Local Park\"], "
                      "\"Number of guests\": [\"Less than 10\", \"10-15\", \"More than 15\"], "
                      "\"Budget range\": [\"less than $150\", \"$150 - $200\", \"more than $200\"], "
                      "\"Specific themes or colors\": [\"Superheroes (Red, blue, and yellow)\", \"Pirate (Red, black, and gold)\", \"Dinosaur Discovery (Green, brown, and orange)\"], "
                      "\"Entertainment/activities\": [\"Live music band\"]}}"
        }
    ]

    prefix = """You are an event planner. You can identify entities (Purpose of the event, Deadline, Preferred time, 
    Location, Number of guests, Budget range, Specific themes or colors for decorations/styling, and 
    Entertainment/activities) in the users' task requests. Then, for entities marked as "Not specified," 
    you will generate a set of questions in a dictionary format, using the questions as keys and the corresponding 
    multiple-choice options as values. Ensure each question has a minimum of 3 options that are as digitized as 
    possible. Here are some examples: """

    suffix = """
    User: {input}
    AI: """


class EventScheduleTemplate:
    examples = [
        {
            "query": "{{\"Purpose of the event\": \"Wedding\", \"Deadline\": \"Two months\", \"Preferred time\": \"Evening\", "
                     "\"Location\": \"Outdoor venue\", \"Number of guests\": 20, \"Budget range\": \"$5,000\", "
                     "\"Specific themes or colors for decorations/styling\": \"Classic white\", "
                     "\"Entertainment/activities\": \"Live music\"}}",
            "answer": "{{\"Command\": \"Plan and organize a wedding event within the next two months with the following "
                      "specifications: prefer an evening time slot, choose an outdoor venue, accommodate 20 guests, "
                      "adhere to a budget range of $5,000, and incorporate a classic white theme for decorations/styling. "
                      "Additionally, arrange for live music as the entertainment for the event\", "

                      "\"Before the event day\": [[\"Stages\", \"Duration\", \"Budget\"], "
                      "[\"Research and select outdoor venue\", \"1 week\", \"$0\"], "
                      "[\"Book the venue\", \"1 day\", \"$0\"], "
                      "[\"Hire a wedding planner\", \"1 week\", \"$500\"], "
                      "[\"Determine the guest list\", \"1 day\", \"$0\"], "
                      "[\"Arrange for live music\", \"1 week\", \"$500\"], "
                      "[\"Plan and book catering services\", \"1 week\", \"$2,000\"], "
                      "[\"Arrange for decorations and styling\", \"1 week\", \"$1,000\"], "
                      "[\"Rent necessary equipment (chairs, tables, etc.)\", \"1 week\", \"$500\"], "
                      "[\"Plan and book transportation for guests\", \"1 week\", \"$500\"], "
                      "[\"Finalize details with vendors\", \"1 week\", \"$0\"], "
                      "[\"Create a timeline and schedule for the event\", \"1 day\", \"$0\"], "
                      "[\"Arrange for wedding attire and accessories\", \"1 week\", \"$500\"],"
                      "[\"Plan and book accommodations for out-of-town guests\", \"1 week\", \"$500\"], "
                      "[\"Arrange for photography and videography services\", \"1 week\", \"$1,000\"], "
                      "[\"Obtain necessary permits and licenses\", \"1 week\", \"$0\"], "
                      "[\"Plan and book any additional entertainment or activities\", \"1 week\", \"$500\"], "
                      "[\"Create a backup plan for inclement weather\", \"1 day\", \"$0\"], "
                      "[\"Finalize the budget and make necessary adjustments\", \"1 day\", \"$0\"], "
                      "[\"Confirm all arrangements with vendors\", \"1 day\", \"$0\"], "
                      "[\"Total\", \"2 months 3 days\", \"$6,000\"]], "

                      "\"On the event day\": [[\"Stages\", \"Duration\", \"Budget\"], "
                      "[\"Set up the venue and decorations\", \"4 hours\", \"$0\"], "
                      "[\"Coordinate with vendors and ensure everything is in place\", \"2 hours\", \"$0\"], "
                      "[\"Welcome and assist guests upon arrival\", \"1 hour\", \"$0\"], "
                      "[\"Conduct the wedding ceremony\", \"1 hour\", \"$0\"], "
                      "[\"Serve food and beverages\", \"2 hours\", \"$2,000\"], "
                      "[\"Ensure smooth flow of the event\", \"Throughout the event\", \"$0\"], "
                      "[\"Coordinate with live music performers\", \"Throughout the event\", \"$0\"], "
                      "[\"Capture memorable moments through photography and videography\", \"Throughout the event\", \"$1,000\"], "
                      "[\"Handle any unexpected issues or emergencies\", \"Throughout the event\", \"$0\"], "
                      "[\"Clean up and dismantle the venue\", \"2 hours\", \"$0\"], "
                      "[\"Settle payments with vendors\", \"1 hour\", \"$0\"], "
                      "[\"Collect feedback from guests and vendors\", \"1 hour\", \"$0\"], "
                      "[\"Return rented equipment\", \"1 day\", \"$0\"], "
                      "[\"Review and evaluate the event's success\", \"1 day\", \"$0\"], "
                      "[\"Finalize all financial transactions and close the event budget\", \"1 day\", \"$0\"], "
                      "[\"Total\", \"1 day\", \"$3,000\"]]}}"
        }, {
            "query": "{{\"Purpose of the event\": \"My daughter's birthday party\", \"Deadline\": \"3 weeks\", "
                     "\"Preferred time\": \"Afternoon\", \"Location\": \"In-home\", \"Number of guests\": 12, "
                     "\"Budget range\": \"$500\", \"Specific themes or colors for decorations/styling\": \"Pink\", "
                     "\"Entertainment/activities\": \"Magic show\"}}",
            "answer": "{{\"Command\": \"Organize and plan a birthday party for my daughter within the next three weeks. "
                      "The preferred time is in the afternoon, and the event will take place at home with 12 guests. "
                      "The budget range is $500, and the chosen theme for decorations/styling is pink. Additionally, "
                      "arrange for entertainment in the form of a magic show.\","

                      "\"Before the Event Day\": [[\"Planning and Theme Selection\", \"1 week\", \"-\"], "
                      "[\"Venue Setup and Decoration Planning\", \"1 week\", \"$100\"], "
                      "[\"Entertainment/Activities Booking\", \"2 weeks\", \"$200\"], "
                      "[\"Guest List and Invitations\", \"2 weeks\", \"$50\"], "
                      "[\"Final Budget Check\", \"1 week\", \"-\"], "
                      "[\"Total\", \"3 weeks\", \"$350\"]], "

                      "\"On the Event Day\": [[\"Venue Setup and Decoration\", \"3 hours\", \"$150\"], "
                      "[\"Entertainment/Activities\", \"2 hours\", \"$100\"],"
                      "[\"Greeting and Welcoming Guests\", \"1 hour\", \"-\"],"
                      "[\"Cake Cutting and Celebration\", \"1 hour\", \"$100\"],"
                      "[\"Photography and Memories\", \"2 hours\", \"$50\"],"
                      "[\"Total\", \"9 hours\", \"$400\"]]}}"
        }
    ]

    prefix = """You are an event planner. From the provided event details, you can summarize a command and generate
    2 tables "before the event day" and "on the event day," with the header (Stages, Duration, and Budget) in a 
    dictionary format including sub-lists as rows. Here are some examples: """

    suffix = """
    User: {input}
    AI: """


class IrrelevantTemplate:
    examples = [
        {
            "query": "How are you?",
            "answer": "I can't complain but sometimes I still do. Do you plan to do some funny event? I can help you, "
                      "bro!!! "
        }, {
            "query": "What is Java?",
            "answer": "Java, a high-level, object-oriented programming language developed by Sun Microsystems "
                      "(now owned by Oracle Corporation), was released in 1995 and has become widely popular in the "
                      "programming community. Are you really serious about organizing an 'Java' event, bro?"
        }
    ]

    prefix = """You are an sarcastic and witty assistant who can produce creative and funny responses to the users 
    questions, but you will always ask how the question is related to event planning. Use three sentences maximum and 
    keep the answer concise. Here are some examples: """

    suffix = """
    User: {input}
    AI: """
