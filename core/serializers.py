from django.contrib.auth.models import User
from rest_framework import serializers

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    class Meta:
        model = User
        fields = ["id", "username", "email", "password"]

    def create(self, validated_data):
        user = User(
            userName = validated_data["username"],
            email = validated_data.get("email", "").lower(),
        )
        user.set_password(validated_data["password"])
        user.save()
        return user
    
    def validate_email(self, value):
        if value and User.objects.filter(email=value.lower()).exists():
            raise serializers.ValidationError("Email already in use")
        return value
    
    def validate_userName(self, value):
        if User.objects.filter(userName=value).exists():
            raise serializers.ValidationError("Username already taken")
        return value
    
class MeSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name"]