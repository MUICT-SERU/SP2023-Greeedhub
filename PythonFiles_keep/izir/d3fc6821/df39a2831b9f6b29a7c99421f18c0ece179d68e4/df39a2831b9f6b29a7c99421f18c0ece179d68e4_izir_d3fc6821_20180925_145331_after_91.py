"""First API, local access only"""
import izi


@izi.local()
def happy_birthday(name: izi.types.text, age: izi.types.number, izi_timer=3):
    """Says happy birthday to a user"""
    return {'message': 'Happy {0} Birthday {1}!'.format(age, name),
            'took': float(izi_timer)}
