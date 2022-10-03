#import boto3
from dynamodb_operations import update_resident,delete_resident,get_all_residents,get_resident_doses,get_image_status,set_image_status_code
#from operations import get_image_number
# def create_residents_table(dynamodb=None):
#     if not dynamodb:
#         #This is just for local test use
#         dynamodb = boto3.resource('dynamodb', endpoint_url="http://localhost:8000")

#     table = dynamodb.create_table(
#         TableName='Residents',
#         KeySchema=[
#             {
#                 'AttributeName': 'residentid',
#                 'KeyType': 'HASH'  # Partition key
#             }
#         ],
#         AttributeDefinitions=[
#             {
#                 'AttributeName': 'residentid',
#                 'AttributeType': 'N'
#             }

#         ],
#         ProvisionedThroughput={
#             'ReadCapacityUnits': 50,
#             'WriteCapacityUnits': 10
#         }
#     )
#     return table
status_code_dic = {"0":"1","1":"2","2":"1","3":"3","4":"1","5":"2","6":"1"}
status_code_add = {"0":"1","1":"3","2":"3","3":"7","4":"5","5":"7","6":"7"}
status_code_del=   {("1","1"):"0",("1","3"):"2",("1","5"):"4",("1","7"):"6",
                    ("2","2"):"0",("2","3"):"1",("2","6"):"4",("2","7"):"5",
                    ("3","4"):"0",("3","5"):"1",("3","6"):"2",("3","7"):"3"}
def get_image_number(id):
    status_code = get_image_status(id)
    status_suffix = status_code_dic[status_code]
    return (status_suffix,status_code)
def set_image_status(id,info,add=True):
    if add:
        #print(info[1])
        status_code = status_code_add[info[1]]
        #print(status_code)
        set_image_status_code(id,status_code)
    else:
        status_code = status_code_del[info]
        set_image_status_code(id,status_code)

if __name__ == '__main__':
    print("")
    
    