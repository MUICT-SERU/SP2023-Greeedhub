"""First izi API (local and HTTP access)"""
import izi


@izi.get(examples='name=ViTuocGia&age=26')
@izi.local()
def happy_birthday(name: izi.types.text, age: izi.types.number, izi_timer=3):
    """Says happy birthday to a user"""
    return {'message': 'Happy {0} Birthday {1}!'.format(age, name),
            'took': float(izi_timer)}
