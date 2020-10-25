import sys
import boto3
import logging
import argparse
import jinja2
from python_terraform import *

logging.basicConfig(level=logging.DEBUG)
logging.disable()

def parse_arguments():
    # get command line arguments
    parser = argparse.ArgumentParser('A tool to learn Terraform and AWS SNS')

    subparsers = parser.add_subparsers(title='main actions', description='valid actions to execute', metavar='action')
    subparser_list = subparsers.add_parser('list', help='list topics or subscriptions to a topic')
    subparser_list.add_argument('list', help='pick to either list topics or subscriptions', metavar='list', choices=['topics', 'subs'])


    subparser_create = subparsers.add_parser('create', help='create topics or subscriptions to a topic')
    subparser_create.add_argument('create', help='pick to either create topics or subscriptions', metavar='create', choices=['topic', 'sub'])

    # TODO: remove this option and just use Terraform's destroy ability?
    #subparser_delete = subparsers.add_parser('delete', help='delete topics or subscriptions to a topic')
    #subparser_delete.add_argument('delete', help='pick to either delete topics or subscriptions', metavar='delete', choices=['topic', 'sub'])

    subparser_publish = subparsers.add_parser('publish', help='publish a message to a topic')    
    subparser_publish.add_argument('publish', help='publish a message to a topic', metavar='publish', nargs='*')    

    subparser_manage = subparsers.add_parser('manage', help='manage the deployment or destruction of resources')    
    subparser_manage.add_argument('manage', help='manage the deployment or destruction of resources', metavar='manage', choices=['deploy', 'destroy'])    
 
    # parse args
    args = parser.parse_args()

    # if no arguments, print help
    if len(sys.argv) < 2:
        parser.print_help()
        exit(1)
  
    return args


def list_topics(client):
    logging.debug('Now entering list topics')
    topics = client.list_topics()['Topics']

    print('Now listing available topics:')
    for topic in topics:
        print(topic)
    

# FIXME: Sort subs based on topic of ARN        
def list_subs(client):
    logging.debug('Now entering list subs')

    print('Which topic would you like to list the subscriptions for?:')
    list_topics(client)

    topic_arn = input('arn: ')

    # May be working? May not be working...
    subs = client.list_subscriptions()
    print(subs)

def render_template(**kwargs):
    logging.debug('Now entering render template')
    template_loader = jinja2.FileSystemLoader(searchpath='./templates/')
    template_env = jinja2.Environment(loader=template_loader)
    template_file = kwargs['name_of_template']
    template = template_env.get_template(template_file)
    if kwargs['name_of_template'] == 'sns_topic.tf':
        output_text = template.render(topic_name=kwargs['topic_name'])
    elif kwargs['name_of_template'] == 'sub_topic.tf':
        output_text = template.render(sub_name=kwargs['sub_name'], topic_arn=kwargs['topic_arn'], phone_number=kwargs['phone_number'])
    elif kwargs['name_of_template'] == 'provider.tf':
        output_text = template.render(region=kwargs['region'])

    return output_text

def write_to_file(output, name):
    with open(name + '.tf', 'w') as f:
        f.write(output)
        f.close()
    
# Create a topic based on a Terraform template    
def create_topic(client):
    logging.debug('Now entering create topic')

    print('What do you want to name the topic?')
    topic_name = input('> ')

    output = render_template(name_of_template='sns_topic.tf', topic_name=topic_name)

    write_to_file(output, topic_name)

    print('Topic file created')

def create_sub(client):
    logging.debug('Now entering create sub')

    list_topics(client)

    # Get variables
    print('Which topic do you want to add a subscription to?')
    topic_arn = input('(arn) > ')
    print('What do you want to name the subscription?')
    sub_name = input('> ')
    print('What phone number do you want to use for the subscription? format=+1AAABBBCCCC')
    phone_number = input('> ')

    output = render_template(name_of_template='sub_topic.tf', sub_name=sub_name, topic_arn=topic_arn, phone_number=phone_number)

    write_to_file(output, sub_name)

    print('Subscription file created')

def publish_message(client, message):
    logging.debug('Now entering publish message')

    list_topics(client)

    print('What topic do you want to publish to?')
    topic_arn = input('(arn) > ')

    # convert the message list to a string
    message = ' '.join(message)

    print('Sending "%s" to "%s"' % (message, topic_arn))
    confirmation = input('(y/n) > ')
    if confirmation == 'y':
        response = client.publish(TopicArn=topic_arn, Message=message)

        # TODO: error handling based on response code
        print('Sent message!')


def set_up_terraform():
    t = Terraform(working_dir='./')
    t.cmd('init')
    return t
    
def deploy_tf_files(client):
    logging.debug('Now entering deploy tf files')

    # pick region to deploy to
    print('What region do you want to deploy to?')
    region = input('> ')

    # create the provider Terraform file
    output = render_template(name_of_template='provider.tf', region=region)

    # write to a new provider file
    write_to_file(output, 'provider')

    print('Provider file created')

    print('Now deploying Terraform files created')
    t = set_up_terraform()
    t.apply(capture_output=False, no_color=None)

def destroy_tf_files(client):
    logging.debug('Now entering destroy tf files')

    t = set_up_terraform()
    t.destroy(capture_output=False, no_color=None)

    print('Destruction of resources complete')

def main():
    args = vars(parse_arguments())

    logging.debug(args)

    client = boto3.client('sns')

    if 'list' in args:
        if args['list'] == 'topics':
            list_topics(client)

        else:
            list_subs(client)

    elif 'create' in args:
        if args['create'] == 'topic':
            create_topic(client)

        else:
            create_sub(client)

    elif 'publish' in args:
        message = args['publish']
        publish_message(client, message)

    elif 'manage' in args:
        if args['manage'] == 'deploy':
            deploy_tf_files(client)
        else:
            destroy_tf_files(client)
        

if __name__ == "__main__":
    main()

    
