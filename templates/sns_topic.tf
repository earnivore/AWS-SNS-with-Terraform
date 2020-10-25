resource "aws_sns_topic" "{{ topic_name }}" {
  name = "{{ topic_name }}"
}

