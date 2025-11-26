"""
Tiny set of intent training examples. This file is used by the training script
to build a minimal intent classifier. Add more phrases for better accuracy.
"""
INTENT_EXAMPLES = {
    'waiting_time': [
        'how long will i wait',
        'what is my waiting time',
        'how much time until my turn',
        'how long is the wait',
        'waiting time'
    ],
    'queue_position': [
        'what is my position',
        "where am i in the queue",
        'how many ahead of me',
        'people ahead of me',
        'what is my queue position'
    ],
    'who_is_my_doctor': [
        'who is my doctor',
        "who's my doctor",
        'who is my primary',
        'who is my pcp',
        'my doctor'
    ],
    'appointments': [
        'my bookings',
        'my appointments',
        'list my appointments',
        'do i have any appointments'
    ],
    'bed_holds': [
        'do i have a bed hold',
        'my bed hold status',
        'is a bed held for me',
        'bed holds'
    ],
    'smalltalk': [
        'hello',
        'how are you',
        'thank you',
        'bye'
    ]
}
