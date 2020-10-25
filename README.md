# AWS-SNS-with-Terraform
A fun tutorial to introduce the Terraform tool using Amazon Web Service's Simple Notification Service with SMS

## Requirements
- HashiCorp Terraform (https://www.terraform.io/downloads.html)

## Usage
```
usage: A tool to learn Terraform and AWS SNS [-h] action ...

optional arguments:
  -h, --help  show this help message and exit

main actions:
  valid actions to execute

  action
    list      list topics or subscriptions to a topic
    create    create topics or subscriptions to a topic
    publish   publish a message to a topic
    manage    manage the deployment or destruction of resources
```

AWS SNS consists of topics and subscriptions. Any endpoint subscribed to a topic will receive messages published to that topic.

The workflow looks something like:
1. Create a SNS topic
2. Add subscriptions to that topic with SMS endpoints
3. Publish messages to the topic and therefore the SMS endpoints

With this script it can be broken downt to:

Create a SNS topic
```
python main.py create topic
```

Once the topic Terraform file is created, deploy the topic
```
python main.py manage deploy
```

With a topic now created, we can add a subscription to that topic
```
python main.py create sub
```

Now deploy the subscription
```
python main.py manage deploy
```

And finally publish messages subscriptions of the topic
```
python main.py publish this is my message here!
```

To destroy, use the following command and remove all `.tf` files from the repository working directory
```
python main.py manage destroy
```

## License
This project is licensed under the terms of the GNU General Public License.

