#pragma once

#include "ROSBridgeSrv.h"

namespace test_package
{
	class SetBool : public FROSBridgeSrv
	{
	public:
		SetBool()
		{
			SrvType = TEXT("test_package/SetBool");
		}

		class Request : public SrvRequest
		{
		private:
			uint8 Data;
					
		public:
			Request(){ }
			Request(uint8 InData)
				:
				Data(InData) { }
			
			
			// Getters 
			uint8 GetData() const { return Data; }
			
			
			// Setters 
			void SetData(uint8 InData) { Data = InData; }
			
			
			virtual void FromJson(TSharedPtr<FJsonObject> JsonObject) override
			{
				Data = JsonObject->GetNumberField(TEXT("data"));

			}
			
			static Request GetFromJson(TSharedPtr<FJsonObject> JsonObject)
			{
				Request Req;
				Req.FromJson(JsonObject);
				return Req;
			}
			
//			### TOSTRING ###
			
			virtual TSharedPtr<FJsonObject> ToJsonObject() const
			{
				TSharedPtr<FJsonObject> Object = MakeShareable<FJsonObject>(new FJsonObject());

				Object->SetNumberField(TEXT("data"), Data);

				return Object;

			}
		};
		
		class Response : public SrvResponse
		{
		private:
			uint8 Success;
			FString Message;
			
			
		public:
			Response(){ }
			Request(uint8 InSuccess,
				FString InMessage)
				:
				Success(InSuccess),
				Message(InMessage) { }
			
			
			// Getters 
			uint8 GetSuccess() const { return Success; }
			FString GetMessage() const { return Message; }
			
			
			// Setters 
			void SetSuccess(uint8 InSuccess) { Success = InSuccess; }
			void SetMessage(FString InMessage) { Message = InMessage; }
			
			
			virtual void FromJson(TSharedPtr<FJsonObject> JsonObject) override
			{
				Success = JsonObject->GetNumberField(TEXT("success"));

				Message = JsonObject->GetStringField(TEXT("message"));

			}
			
			static Response GetFromJson(TSharedPtr<FJsonObject> JsonObject)
			{
				Response Resp; 
				Resp.FromJson(JsonObject);
				return Resp;
			}			
			
//			### TOSTRING ###
			
			virtual TSharedPtr<FJsonObject> ToJsonObject() const
			{
				TSharedPtr<FJsonObject> Object = MakeShareable<FJsonObject>(new FJsonObject());

				Object->SetNumberField(TEXT("success"), Success);

				Object->SetStringField(TEXT("message"), Message);

				return Object;

			}
		};
		
	};
	
}