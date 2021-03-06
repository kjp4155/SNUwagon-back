from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from utils.response import generate_response
from api.serializers import QuestionPostSerializer, InformationPostSerializer
from api.models import QuestionPost, Profile, User, InformationPost, QuestionAnswer
from django.utils import timezone
import operator


def cleanup_question():
    every_questions = QuestionPost.objects.filter(due__lt=timezone.localtime()).order_by('-created')
    for question in every_questions:
        author = question.author
        answer_cnt = QuestionAnswer.objects.filter(question=question).count()
        if answer_cnt == 0:
            author.credit += question.bounty
            author.save()
            question.delete()


@swagger_auto_schema(methods=['get'], responses={200: QuestionPostSerializer})
@api_view(['GET'])
def questions(request):
    cleanup_question()
    every_questions = QuestionPost.objects.filter(due__gte=timezone.localtime()).order_by('-created')
    serializer = QuestionPostSerializer(every_questions, many=True)

    for x in serializer.data:
        x.pop('content', None)
        x['author'] = Profile.objects.get(pk=x['author']).user.username

    return generate_response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
def questions_with_tag(request, tag):
    cleanup_question()
    every_questions = QuestionPost.objects.\
        filter(tags__contains=[tag], due__gte=timezone.localtime()).order_by('-created')
    serializer = QuestionPostSerializer(every_questions, many=True)

    for x in serializer.data:
        x.pop('content', None)
        x['author'] = Profile.objects.get(pk=x['author']).user.username

    return generate_response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
def questions_with_type(request, type):
    return Response({'message': 'NOT IMPLEMENTED'}, status=status.HTTP_501_NOT_IMPLEMENTED)


@api_view(['GET'])
def questions_with_title(request, title):
    cleanup_question()
    every_questions = QuestionPost.objects.\
        filter(title__icontains=title, due__gte=timezone.localtime()).order_by('-created')
    serializer = QuestionPostSerializer(every_questions, many=True)

    for x in serializer.data:
        x.pop('content', None)
        x['author'] = Profile.objects.get(pk=x['author']).user.username

    return generate_response(serializer.data, status=status.HTTP_200_OK)


@swagger_auto_schema(methods=['get'], responses={200: InformationPostSerializer})
@api_view(['GET'])
def informations(request):
    every_informations = InformationPost.objects.\
        filter(due__gte=timezone.localtime()).\
        order_by('-created')
    serializer = InformationPostSerializer(every_informations, many=True)

    for x in serializer.data:
        x.pop('content', None)
        x.pop('hidden_content', None)
        x['author'] = Profile.objects.get(pk=x['author']).user.username

    return generate_response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
def informations_with_tag(request, tag):
    every_informations = InformationPost.objects.\
        filter(tags__contains=[tag], due__gte=timezone.localtime()).\
        order_by('-created')
    serializer = InformationPostSerializer(every_informations, many=True)

    for x in serializer.data:
        x.pop('content', None)
        x.pop('hidden_content', None)
        x['author'] = Profile.objects.get(pk=x['author']).user.username

    return generate_response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
def informations_with_type(request, type):
    return Response({'message': 'NOT IMPLEMENTED'}, status=status.HTTP_501_NOT_IMPLEMENTED)


@api_view(['GET'])
def informations_with_title(request, title):
    every_informations = InformationPost.objects.\
        filter(title__contains=title, due__gte=timezone.localtime()).\
        order_by('-created')
    serializer = InformationPostSerializer(every_informations, many=True)

    for x in serializer.data:
        x.pop('content', None)
        x.pop('hidden_content', None)
        x['author'] = Profile.objects.get(pk=x['author']).user.username

    return generate_response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
def tags(request):
    tag_dict = {}
    every_informations = InformationPost.objects.all()
    every_questions = QuestionPost.objects.all()

    for info in every_informations:
        for tag in info.tags:
            if tag in tag_dict.keys():
                tag_dict[tag] = tag_dict[tag] + 1
            else:
                tag_dict[tag] = 1

    for question in every_questions:
        for tag in question.tags:
            if tag in tag_dict.keys():
                tag_dict[tag] = tag_dict[tag] + 1
            else:
                tag_dict[tag] = 1

    sortedArr = sorted(tag_dict.items(), key=operator.itemgetter(1), reverse=True)

    data = []
    for x in sortedArr:
        data.append(x[0])
    response_data = {'tags': data}

    return generate_response(response_data, status=status.HTTP_200_OK)
