from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from models import Item
from forms import ItemForm
from django.http import HttpResponseRedirect

@login_required
def index(request):
    """Show the home page of the todo list app"""    
    todo_items = Item.objects.filter(user__exact=request.user)
    
    order = request.GET.get('order')
    if order == 'priority':
        todo_items = todo_items.order_by('priority', '-created')
    elif order == 'due':
        todo_items = todo_items.order_by('-due', '-created')
    else: # This also executes when order = created
        todo_items = todo_items.order_by('-created')
        order = 'created'
        
    return render_to_response('todo/index.html', {'user': request.user, 
        'todo_items': todo_items, 'order': order}, context_instance=RequestContext(request))

@login_required		
def delete(request, pk):
    """Deletes a todo item"""
    item = Item.objects.filter(user__exact=request.user).filter(pk=pk)
    item.delete()
    return HttpResponseRedirect('/todo/')

@login_required    
def add(request):
    """Display the 'add an item' form & save the item if validation passed"""

    if request.method == 'POST':
        form = ItemForm(request.POST.copy())
        
        if form.is_valid():            
            item = form.save(commit=False)
            item.user = request.user
            item.save()
            return HttpResponseRedirect("/todo/")
    else:
        form = ItemForm()

    return render_to_response("todo/item.html", {
        'form' : form, 
    },context_instance=RequestContext(request))

@login_required    
def edit(request, pk):
    """Edits a todo item"""
    
    if request.method == 'POST':
        form = ItemForm(request.POST.copy())
        
        if form.is_valid():            
            edited_item = form.save(commit=False)
            original_item = Item.objects.filter(user__exact=request.user).get(pk__exact=pk)
            edited_item.user = original_item.user
            edited_item.pk = original_item.pk
            edited_item.created = original_item.created
            edited_item.save()
            return HttpResponseRedirect("/todo/")
    else:
        item = Item.objects.get(pk__exact = pk)
        form = ItemForm(instance=item)
    
    return render_to_response("todo/item.html", {
        'form' : form, 
    },context_instance=RequestContext(request))