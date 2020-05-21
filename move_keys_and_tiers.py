from simplekeys.models import Key
from django.contrib.auth.models import User
from profiles.models import KEY_TIERS


for key in Key.objects.all():
    try:
        user = User.objects.get(email=key.email)
    except Exception as e:
        print(key.email, e)
        continue

    if user.profile.api_key:
        key.delete()
        continue

    user.profile.api_key = key.key

    if key.status == "s":
        user.profile.api_tier = "suspended"
    elif key.status == "a":
        if key.tier.slug == "legacy":
            user.profile.api_tier = "silver"
        elif key.tier.slug not in KEY_TIERS:
            print(key.tier)
        else:
            user.profile.api_tier = key.tier.slug
        user.profile.save()

    #print(f'setting {user} key to {user.profile.api_tier}')
