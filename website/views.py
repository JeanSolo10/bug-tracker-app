from distutils.log import error
from nis import cat
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from sqlalchemy import desc
from .models import Project, User, Ticket, Comment
from . import db
from collections import Counter
from flask_sqlalchemy import Pagination
import types
from werkzeug.security import generate_password_hash

views = Blueprint('views', __name__)

@views.route('/')
@login_required
def home():
    priority_occurrences = [ticket.priority for ticket in current_user.tickets]
    priority_labels = ["Low", "Medium", "High"]
    priority_values = [Counter(priority_occurrences)["Low"], Counter(priority_occurrences)["Medium"], Counter(priority_occurrences)["High"]]
    status_occurances = [ticket.status for ticket in current_user.tickets]
    status_labels = ["New", "In Progress", "Additional Info Req."]
    status_values = [Counter(status_occurances)["New"], Counter(status_occurances)["In Progress"], Counter(status_occurances)["Additional Info Required"]]
    return render_template("home.html", user=current_user, priority_labels=priority_labels, priority_values=priority_values, status_labels=status_labels, status_values=status_values)

# projects routing #
@views.route('/projects/page/<int:page_num>')
@login_required
def projects(page_num):
    
    projectsData = current_user.projects
    # sort by date dec
    projectsData.reverse()

    # projects pagination
    projects_per_page = 10
    start = (page_num - 1) * projects_per_page
    end = start + projects_per_page
    items = projectsData[start:end]
    projectsPagination = Pagination(None, page_num, projects_per_page, len(projectsData), items)

    # tickets pagination
    has_next_page = projectsPagination.has_next
    has_prev_page = projectsPagination.has_prev
    next_page = projectsPagination.next_num
    prev_page = projectsPagination.prev_num

    return render_template("projects.html", 
                            user=current_user,
                            has_next_page=has_next_page,
                            has_prev_page=has_prev_page,
                            next_page=next_page,
                            prev_page=prev_page,
                            projects=projectsPagination
                            )

@views.route('/projects/new', methods=['GET', 'POST'])
@login_required
def new_project():
    currForm = types.SimpleNamespace()

    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        owner_id = current_user.id
        members = request.form.getlist('members')
        
        if name:
            currForm.name = name
        if description:
            currForm.description = description

        project = Project.query.filter_by(name=name).first()

        if not name:
            flash('Enter name', category='error')
        elif project:
            flash('Name already exists!', category='error')
        elif not description:
            flash('Enter description', category='error')
        elif len(members) < 1:
            flash('You must select at least 1 member', category='error')
        elif len(name) < 2:
            flash('Project Name must be greater than 1 character', category='error')
        elif len(description) < 4:
            flash('Project Description must be greater than 3 character', category='error')
        else:
            new_project = Project(name=name, description=description, owner_id=owner_id)
            db.session.add(new_project)
            # add members
            if members:
                for id in members:
                    member = User.query.filter_by(id=id).first()
                    new_project.members.append(member)
            db.session.commit()
            flash('Project created!', category='success')
            return redirect(url_for('views.projects', page_num=1))

    # handle GET request
    users = load_all_users()
    return render_template("new_project.html", user=current_user, userList=users, form=currForm)    

@views.route('/projects/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_project(id):
    project_info = types.SimpleNamespace()
    project = Project.query.get_or_404(id)

    project_info.name = project.name
    project_info.description = project.description
    project_info.owner_id = project.owner_id
    project_info.members = project.members
    users = list(set(project.members) ^ set(load_all_users()))

    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        owner_id = request.form.get('owner_id')
        members = request.form.getlist('members')

        if not name:
            flash('Enter name', category='error')
        elif not description:
            flash('Enter description', category='error')
        elif len(members) < 1:
            flash('You must select at least 1 member', category='error')
        elif len(name) < 2:
            flash('Project Name must be greater than 1 character', category='error')
        elif len(description) < 4:
            flash('Project Description must be greater than 3 character', category='error')
        else:
            project.name = name
            project.description = description
            project.owner_id = owner_id
            list_members = []
            for id in members:
                member = User.query.filter_by(id=id).first()
                list_members.append(member)
            project.members = list_members
            db.session.add(project)
            db.session.commit()
            flash('Project updated!', category='success')
            return redirect(url_for('views.project_details', id=project.id, m_page_num=1, t_page_num=1))


    return render_template("edit_project.html", user=current_user, project_info=project_info, users=users)

@views.route('/projects/<id>/details/members/<int:m_page_num>/tickets/<int:t_page_num>', methods=['GET', 'POST'])
@login_required
def project_details(id, t_page_num, m_page_num):
    project = Project.query.filter_by(id=id).first()
    tickets = Ticket.query.filter_by(project_reference=id).order_by(Ticket.date.desc()).paginate(per_page=6, page=t_page_num, error_out=True)
    members = project.members
    
    members_per_page = 6
    start = (m_page_num - 1) * members_per_page
    end = start + members_per_page
    items = members[start:end]
    membersPagination = Pagination(None, m_page_num, members_per_page, len(members), items)

    # members pagination
    members_has_next_page = membersPagination.has_next
    members_has_prev_page = membersPagination.has_prev
    members_next_page = membersPagination.next_num
    members_prev_page = membersPagination.prev_num

    # tickets pagination
    has_next_page = tickets.has_next
    has_prev_page = tickets.has_prev
    next_page = tickets.next_num
    prev_page = tickets.prev_num
    
    return render_template("project_details.html", 
                            user=current_user, 
                            project=project, 
                            members=membersPagination, 
                            tickets=tickets, 
                            has_next_page=has_next_page, 
                            has_prev_page=has_prev_page, 
                            next_page=next_page, 
                            prev_page=prev_page,
                            members_has_next_page=members_has_next_page, 
                            members_has_prev_page=members_has_prev_page, 
                            members_next_page=members_next_page, 
                            members_prev_page=members_prev_page
                            )

def load_all_users():
    return User.query.all()

# projects routing #

# tickets routing #
@views.route('/tickets/page/<int:page_num>')
@login_required
def tickets(page_num):
    tickets = Ticket.query.filter_by(assigned_to=current_user.id).order_by(Ticket.date.desc()).paginate(per_page=10, page=page_num, error_out=True)
    # tickets pagination
    has_next_page = tickets.has_next
    has_prev_page = tickets.has_prev
    next_page = tickets.next_num
    prev_page = tickets.prev_num
    return render_template("tickets.html",
                            user=current_user,
                            has_next_page=has_next_page,
                            has_prev_page=has_prev_page,
                            next_page=next_page,
                            prev_page=prev_page,
                            tickets=tickets
                            )

@views.route('/project/<id>/ticket/<ticket_id>', methods=['GET', 'POST'])
@login_required
def ticket_details(id, ticket_id):
    ticket = Ticket.query.filter_by(id=ticket_id).first()
    comments = Comment.query.filter_by(ticket_reference=ticket_id)
    
    if request.method == 'POST':
        comment = request.form.get('comment')

        if len(comment) < 1:
            flash('Comment is too short!', category='error')
        else:
            new_comment = Comment(comment=comment, author=current_user.id, ticket_reference=ticket_id)
            db.session.add(new_comment)
            db.session.commit()
            flash('Comment added!', category='success')

    
    return render_template("ticket_details.html", user=current_user, ticket=ticket, comments=comments)

@views.route('/project/<id>/ticket/new/', methods=['GET', 'POST'])
@login_required
def new_ticket(id):
    currForm = types.SimpleNamespace()
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        assigned_to = request.form.getlist('developer')[0]
        type = request.form.getlist('type')[0]
        priority = request.form.getlist('priority')[0]
        status = request.form.getlist('status')[0]
        submitted_by = current_user.first_name + " " + current_user.last_name
        project_reference = id

        if name:
            currForm.name = name
        if description:
            currForm.description = description
        if assigned_to:
            currForm.assigned_to = assigned_to

        if not name:
            flash('Enter name', category='error')
        elif len(name) < 2:
            flash('Ticket Name must be greater than 1 character', category='error')
        elif assigned_to == 'Select Developer':
            flash('You must select a developer for this ticket', category='error')
        elif not description:
            flash('Enter description', category='error')
        elif len(description) < 4:
            flash('Ticket Description must be greater than 3 character', category='error')
        else:
            new_ticket = Ticket(name=name, description=description, type=type, priority=priority, status=status, submitted_by=submitted_by, project_reference=project_reference, assigned_to=assigned_to)
            db.session.add(new_ticket)
            db.session.commit()
            flash('Ticket created!', category='success')
            return redirect(url_for('views.project_details', id=id, m_page_num=1, t_page_num=1))
    
    project = Project.query.filter_by(id=id).first()
    
    return render_template("new_ticket.html", user=current_user, project_members=project.members, form=currForm) 

@views.route('/tickets/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_ticket(id):
    ticket_info = types.SimpleNamespace()
    ticket = Ticket.query.get_or_404(id)

    ticket_info.name = ticket.name
    ticket_info.description = ticket.description
    ticket_info.status = ticket.status
    ticket_info.type = ticket.type
    ticket_info.priority = ticket.priority
    ticket_info.assigned_to = ticket.assigned_to
    #users = list(set(ticket.members) ^ set(load_all_users()))

    project = Project.query.filter_by(id=ticket.project_reference).first()
    available_types = ["Bug", "Enhancement"]
    available_priorities = ["Low", "Medium", "High"]
    available_status = ["New", "In Progress", "Additional Info Required", "Resolved"]

    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        assigned_to = request.form.getlist('developer')[0]
        type = request.form.getlist('type')[0]
        priority = request.form.getlist('priority')[0]
        status = request.form.getlist('status')[0]

        if not name:
            flash('Enter name', category='error')
        elif len(name) < 2:
            flash('Ticket Name must be greater than 1 character', category='error')
        elif assigned_to == 'Select Developer':
            flash('You must select a developer for this ticket', category='error')
        elif not description:
            flash('Enter description', category='error')
        elif len(description) < 4:
            flash('Ticket Description must be greater than 3 character', category='error')
        else:
            ticket.name = name
            ticket.description = description
            ticket.assigned_to = assigned_to
            ticket.type = type
            ticket.priority = priority
            ticket.status = status
            
            db.session.add(ticket)
            db.session.commit()
            flash('Ticket updated!', category='success')
            return redirect(url_for('views.ticket_details', id=project.id, ticket_id=ticket.id))


    return render_template("edit_ticket.html", 
                            user=current_user, 
                            ticket_info=ticket_info, 
                            project_members=project.members,
                            available_types=available_types,
                            available_priorities=available_priorities,
                            available_status=available_status) 

# admin routes
# projects routing #
@views.route('/admin/projects/page/<int:page_num>')
@login_required
def admin_projects(page_num):
    projects = Project.query.order_by(Project.date.desc()).paginate(per_page=20, page=page_num, error_out=True)
    # tickets pagination
    has_next_page = projects.has_next
    has_prev_page = projects.has_prev
    next_page = projects.next_num
    prev_page = projects.prev_num

    return render_template("admin_projects.html", 
                            user=current_user,
                            has_next_page=has_next_page,
                            has_prev_page=has_prev_page,
                            next_page=next_page,
                            prev_page=prev_page,
                            projects=projects
                            )

@views.route('/admin/personnel/page/<int:page_num>')
@login_required
def admin_personnel(page_num):
    personnel = User.query.filter(User.role != "admin").paginate(per_page=20, page=page_num, error_out=True)
    print(f'personnel: {personnel}')
    # tickets pagination
    has_next_page = personnel.has_next
    has_prev_page = personnel.has_prev
    next_page = personnel.next_num
    prev_page = personnel.prev_num

    return render_template("admin_personnel.html", 
                            user=current_user,
                            has_next_page=has_next_page,
                            has_prev_page=has_prev_page,
                            next_page=next_page,
                            prev_page=prev_page,
                            personnel=personnel
                            )

@views.route('/project/<int:page_num>/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_project(page_num, id):
    project = Project.query.filter_by(id=id).first()
    if request.method == 'POST':
        if project:
            db.session.delete(project)
            db.session.commit()
            flash('Project deleted successfully!', category='success')
            return redirect(url_for('views.admin_projects', page_num=page_num))


    return render_template('delete_project.html', user=current_user)

@views.route('/personnel/<int:page_num>/<int:id>', methods=['GET', 'POST'])
@login_required
def admin_update_personnel(page_num, id):
    currForm = types.SimpleNamespace()
    user = User.query.filter_by(id=id).first()
    currForm.first_name = user.first_name
    currForm.last_name = user.last_name
    currForm.email = user.email
    currForm.role = user.role

    if request.method == 'POST':
        first_name = request.form.get('firstName')
        last_name = request.form.get('lastName')
        email = request.form.get('email')
        role = request.form.getlist('role')[0]
        password = request.form.get('password')      

        if email:
            currForm.email = email
        if first_name:
            currForm.first_name = first_name
        if last_name:
            currForm.last_name = last_name
        if role:
            currForm.role = role
        if role == 'Select Role':
            flash('You must select a role', category='error')
        elif len(email) < 5:
            flash('Email must be greater than 4 characters', category='error')
        elif len(first_name) < 2:
            flash('First Name must be greater than 1 character', category='error')
        elif len(last_name) < 2:
            flash('Last Name must be greater than 1 character', category='error')
        else:
            user.first_name = first_name
            user.last_name = last_name
            user.email = email
            user.role = role
            if password:
                if len(password) < 7:
                    flash('Password must be at least 7 characters.', category='error')
                    return render_template("admin_update_personnel.html", 
                            user=current_user,
                            form=currForm)
                else:
                    user.password = generate_password_hash(password, method='sha256')
            db.session.add(user)
            db.session.commit()
            flash('User updated successfully!', category='success')
            return redirect(url_for('views.admin_personnel', page_num=page_num))

    return render_template("admin_update_personnel.html", 
                            user=current_user,
                            form=currForm)

@views.route('/personnel/<int:page_num>/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_user(page_num, id):
    user = User.query.filter_by(id=id).first()
    if request.method == 'POST':
        if user:
            db.session.delete(user)
            db.session.commit()
            flash('User deleted successfully!', category='success')
            return redirect(url_for('views.admin_personnel', page_num=page_num))


    return render_template('delete_user.html', user=current_user)
