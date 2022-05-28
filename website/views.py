from distutils.log import error
from nis import cat
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from .models import Project, User, Ticket, Comment
from . import db
from collections import Counter
from flask_sqlalchemy import Pagination

views = Blueprint('views', __name__)

@views.route('/')
@login_required
def home():
    priority_occurrences = [ticket.priority for ticket in current_user.tickets]
    priority_labels = ["Low", "Medium", "High"]
    priority_values = [Counter(priority_occurrences)["Low"], Counter(priority_occurrences)["Medium"], Counter(priority_occurrences)["High"]]
    status_occurances = [ticket.status for ticket in current_user.tickets]
    status_labels = ["New", "In Progress", "Additional Info Required"]
    status_values = [Counter(status_occurances)["New"], Counter(status_occurances)["In Progress"], Counter(status_occurances)["Additional Info Required"]]
    return render_template("home.html", user=current_user, priority_labels=priority_labels, priority_values=priority_values, status_labels=status_labels, status_values=status_values)

# projects routing #
@views.route('/projects')
@login_required
def projects():
    return render_template("projects.html", user=current_user)

@views.route('/projects/new', methods=['GET', 'POST'])
@login_required
def new_project():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        owner_id = current_user.id
        members = request.form.getlist('members')

        if not name:
            flash('Enter name', category='error')
        elif not description:
            flash('Enter description', category='error')
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
            return redirect(url_for('views.projects'))

    # handle GET request
    users = load_all_users()
    return render_template("new_project.html", user=current_user, userList=users)    

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
@views.route('/tickets')
@login_required
def tickets():
    return render_template("tickets.html", user=current_user)

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
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        assigned_to = request.form.getlist('developer')[0]
        type = request.form.getlist('type')[0]
        priority = request.form.getlist('priority')[0]
        status = request.form.getlist('status')[0]
        submitted_by = current_user.first_name + " " + current_user.last_name
        project_reference = id

        if not name:
            flash('Enter name', category='error')
        elif not description:
            flash('Enter description', category='error')
        elif len(name) < 2:
            flash('Project Name must be greater than 1 character', category='error')
        elif len(description) < 4:
            flash('Project Description must be greater than 3 character', category='error')
        else:
            new_ticket = Ticket(name=name, description=description, type=type, priority=priority, status=status, submitted_by=submitted_by, project_reference=project_reference, assigned_to=assigned_to)
            db.session.add(new_ticket)
            db.session.commit()
            flash('Ticket created!', category='success')
            return redirect(url_for('views.project_details', id=id, page_num=1))

    
    project = Project.query.filter_by(id=id).first()
    
    return render_template("new_ticket.html", user=current_user, project_members=project.members) 