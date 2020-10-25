resource "aws_sns_topic_subscription" "{{ sub_name }}" {
  topic_arn = "{{ topic_arn }}"
  protocol = "sms"
  endpoint = "{{ phone_number }}"
}
