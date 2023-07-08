from django.shortcuts import render
from rest_framework import generics, status
# Create your views here.
from .models import *
from .serializers import *
from rest_framework.views import APIView
from rest_framework.response import Response
import logging
from django.db import transaction
import random
from django.views.generic import ListView
import re
inprogress_orders = {}
class ProductView(generics.CreateAPIView):
    queryset = Products.objects.all()
    serializer_class = ProductSerializer

class AllProductsList_1(APIView):

    def get(self, request, format=None):
        products = Products.objects.all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)
    
class Order(generics.CreateAPIView):
    queryset = Orders.objects.all()
    serializer_class = OrderSerializer

class OrderItems(generics.CreateAPIView):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer

class TrackOrders(generics.CreateAPIView):
    queryset = Tracking.objects.all()
    serializer_class = TrackOrderSerializer

class AllOrders(APIView):
    def get(self, request, format=None):
        orders = Orders.objects.all()
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)
    


class WebhookView(APIView):
    logger = logging.getLogger(__name__)
   

    def post(self, request, format=None):
        try:
            data = request.data
            intent = data['queryResult']['intent']['displayName']
            session_id = extract_session_id(data['queryResult']['outputContexts'][0]['name'])
            output_context = data['queryResult']['outputContexts']

            self.logger.info(f"Received webhook request for intent: {intent}")
            self.logger.info(f"Session ID: {session_id}")
            self.logger.info(f"Output Context: {output_context}")

            if intent == 'order.add - context: ongoing-order':
                return self.handle_order_add(data, session_id)
            elif intent == 'order.remove - context: ongoing-order':
                return self.handle_order_remove(data, session_id)
            elif intent == 'track.order - context: ongoing-tracking':
                return self.handle_track_order(data, session_id)
            elif intent == 'order.complete - context: ongoing-order':
                return self.handle_complete_order(data, session_id)
            else:
                return self.handle_unknown_intent(data, session_id)

        except Exception as e:
            self.logger.error(f"Error occurred in webhook: {str(e)}")
            return self.handle_exception(e)

    def handle_order_add(self, data, session_id):
        # Extract parameters specific to the 'order.add' intent
        parameters = data['queryResult']['parameters']
        items = parameters['menu-items']
        quantities = parameters['number']

        

        if len(items) != len(quantities):
            response = {
                'fulfillmentText': 'Sorry I didnt get you. Can you please specify the food items and quantities again',
                # Include any response you want to send back to Dialogflow
            }
        else:
            items_dict = dict(zip(items, quantities))

            if session_id in inprogress_orders:
                current = inprogress_orders[session_id]
                current.update(items_dict)
                inprogress_orders[session_id] = current
            else: 
                inprogress_orders[session_id] = items_dict

            string = string_rep(inprogress_orders[session_id])
            response = {
                'fulfillmentText': f'The following items are in your current order {string}, Would you like anything else?',
                # Include any response you want to send back to Dialogflow
            }

        


        # Your logic for handling the 'order.add' intent
        # Use the extracted parameters and session ID as needed

        
        return Response(response)
    
    def handle_complete_order(self, data, session_id):
        # Extract parameters specific to the 'order.add' intent
        parameters = data['queryResult']['parameters']

        # Your logic for handling the 'order.add' intent
        # Use the extracted parameters and session ID as needed

        if session_id not in inprogress_orders:


            response = {
                'fulfillmentText': 'Im having trouble finding your order, you might have to place another one',
                # Include any response you want to send back to Dialogflow
            }
        else:
            order_items = inprogress_orders[session_id]
            random_integer = random.randrange(1,1000000000)
            try:
           
                # Create a new Orders object
                order = Orders.objects.create(order_key=random_integer)
                order.session_id = session_id
                order.save()
                

                # Iterate over the items_dict and create OrderItem objects
                for item_name, quantity in order_items.items():
                    product = Products.objects.get(name=item_name)
                    OrderItem.objects.create(order=order, product=product, quantity=quantity)

                    

                # Clear the inprogress_orders for the session
                del inprogress_orders[session_id]
                tracked = Tracking.objects.create(order_id=order, status="IN_TRANSIT")

                response = {
                    'fulfillmentText': f'Order {order.order_key} has been placed successfully. This is your total {order.get_total_amount()}. ***This is your Order Id for tracking #{order.id}',
                    # Include any response you want to send back to Dialogflow
                }
            except Exception as e:
                self.logger.error(f"Error occurred while processing the order: {str(e)}")
                response = {
                    'fulfillmentText': 'An error occurred while processing the order',
                    # Include any response you want to send back to Dialogflow
                }

        return Response(response)

    def handle_track_order(self, data, session_id):
        # Extract parameters specific to the 'track.order' intent
        parameters = data['queryResult']['parameters']
        order_id = int(parameters['number'])  # Convert to integer

        order = Orders.objects.get(id=order_id)

        order_content = Tracking.objects.filter(order_id=order).first()


        # Your logic for handling the 'track.order' intent
        # Use the extracted parameters and session ID as needed
        if order_content:
            response = {
                'fulfillmentText': f'Order Status is {order_content.status}',
                # Include any response you want to send back to Dialogflow
            }
            return Response(response)
        else:
            response = {
                'fulfillmentText': 'Order Not found',
            }
            return Response(response)

    def handle_order_remove(self, data, session_id):
        # Extract parameters specific to the 'order.remove' intent
        parameters = data['queryResult']['parameters']
        

        # Your logic for handling the 'order.remove' intent
        # Use the extracted parameters and session ID as needed

        if session_id not in inprogress_orders:

            response = {
                'fulfillmentText': 'Im having trouble finding your order, please place it again',

                # Include any response you want to send back to Dialogflow
            }

        else:
            current_order = inprogress_orders[session_id]
            items = parameters['menu-items']
            removed_items = []
            no_such_items = []
            for item in items:
                if item not in current_order:
                    no_such_items.append(item)
                else:
                    removed_items.append(item)
                    del current_order[item]
                    
            if len(removed_items)>0:
                response = {
                    'fulfillmentText': f'The following items were removed from your order {",".join(removed_items)}',

                    # Include any response you want to send back to Dialogflow
                    }
                
            if len(no_such_items)>0:
                response = {
                    'fulfillmentText': f'Unfortunately your current order doesnt have{",".join(no_such_items)}',

                    # Include any response you want to send back to Dialogflow
                    }
                
            if len(current_order.keys()) == 0:
                response = {
                    'fulfillmentText': 'Your order is empty!!',


                    # Include any response you want to send back to Dialogflow
                    }
            else:
                final_str = string_rep(current_order)
                response = {
                    'fulfillmentText': f'The following items are in your current order {final_str}, Would you like anything else?',
                    # Include any response you want to send back to Dialogflow
                }


                

            
                

            

        return Response(response)

    def handle_unknown_intent(self, data, session_id):
        # Your logic for handling unknown intents
        response = {
            'fulfillmentText': 'Unknown intent handler triggered',
            # Include any response you want to send back to Dialogflow
        }
        return Response(response)

    def handle_exception(self, exc):
        response = {
            'fulfillmentText': 'An error occurred here',
            # Include any error response you want to send back to Dialogflow
        }
        return Response(response)
    
def extract_session_id(session_str):
    match = re.search(r"/sessions/(.*?)/contexts/", session_str)
    if match: 
        extracted_id = match.group(1)
        return extracted_id
    return ""

def string_rep(items_dict):
    return ", ".join([f"{int(value)} {key}" for key, value in items_dict.items()])

class Home(ListView):
    model = Orders
    context_object_name = 'feed'
    template_name = 'api/home.html'