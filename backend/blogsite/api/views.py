from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.db.models import Count
from django.http import JsonResponse
from django.views.generic.detail import BaseDetailView
from django.views.generic.list import BaseListView
from taggit.models import Tag

from api.view_util import obj_to_post, prev_next_post, make_tag_cloud
from blog.models import Post


class ApiPostLV(BaseListView):
    # model = Post

    def get_queryset(self):
        tagname = self.request.GET.get('tagname')
        if tagname:
            qs = Post.objects.filter(tags__name=tagname)
        else:
            qs = Post.objects.all()

        return qs

    def render_to_response(self, context, **response_kwargs):
        qs = context['object_list'] #Post 테이블에서 가져온 모든 레코드를 가져온다.
        postlist = [obj_to_post(obj) for obj in qs]
        return JsonResponse(data=postlist, safe=False, status=200)


class ApiPostDV(BaseDetailView):
    model = Post

    def render_to_response(self, context, **response_kwargs):
        obj = context['object']
        post = obj_to_post(obj)
        post['prev'], post['next'] = prev_next_post(obj)
        return JsonResponse(data=post, safe=True, status=200)


class ApiTagCloudLV(BaseListView):
    # model = Tag
    queryset = Tag.objects.annotate(count=Count('post'))

    def render_to_response(self, context, **response_kwargs):
        qs = context['object_list'] #Post 테이블에서 가져온 모든 레코드를 가져온다.
        # postlist = [obj_to_post(obj) for obj in qs]
        # tagList = []
        # for obj in qs:
        #     tagList.append({
        #         'name': obj.name,
        #     })
        tagList = make_tag_cloud(qs)
        return JsonResponse(data=tagList, safe=False, status=200)


class ApiLoginView(LoginView):

    def form_valid(self, form):
        user = form.get_user()
        login(self.request, user)
        # userDict = vars(user)
        # del userDict['_state'], userDict['password']
        userDict = {
            'id': user.id,
            'username': user.username,
        }
        return JsonResponse(data=userDict, safe=True, status=200)

    def form_invalid(self, form):
        return JsonResponse(data=form.errors, safe=True, status=400)