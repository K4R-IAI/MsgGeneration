#pragma once

#include ROSBridgeMsg.h

#include "std_msgs/String.h"
#include "sensor_msgs/RegionOfInterest.h"

namespace other_msgs
{
	class MyCreativeMessage : public FROSBridgeMsg
	{
		std_msgs::String MyString;
		TArray<FString> MyOtherString;
		uint32 SomeNumber;
		sensor_msgs::RegionOfInterest ROI;
	public:
		MyCreativeMessage()
		{
			MsgType = "other_msgs/MyCreativeMessage";
		}

		MyCreativeMessage
		(
			std_msgs::String InMyString,
			const TArray<FString>& InMyOtherString,
			uint32 InSomeNumber,
			sensor_msgs::RegionOfInterest InROI
		):
			MyString(InMyString),
			MyOtherString(InMyOtherString),
			SomeNumber(InSomeNumber),
			ROI(InROI)
		{
			MsgType = "other_msgs/MyCreativeMessage";
		}

		~MyCreativeMessage() override {}

		std_msgs::String GetMyString() const
		}
			return MyString;
		}

		TArray<FString> GetMyOtherString() const
		}
			return MyOtherString;
		}

		uint32 GetSomeNumber() const
		}
			return SomeNumber;
		}

		sensor_msgs::RegionOfInterest GetROI() const
		}
			return ROI;
		}

		void SetMyString(std_msgs::String InMyString)
		}
			MyString = InMyString;
		}

		void SetMyOtherString(TArray<FString>& InMyOtherString)
		}
			MyOtherString = InMyOtherString;
		}

		void SetSomeNumber(uint32 InSomeNumber)
		}
			SomeNumber = InSomeNumber;
		}

		void SetROI(sensor_msgs::RegionOfInterest InROI)
		}
			ROI = InROI;
		}

		virtual void FromJson(TSharedPtr<FJsonObject> JsonObject) override
		{
			MyString = std_msgs::String::GetFromJson(JsonObject->GetObjectField(TEXT("mystring")));

			TArray<TSharedPtr<FJsonValue>> ValuesPtrArr;

			MyOtherString.Empty();
			ValuesPtrArr = JsonObject->GetArrayField(TEXT("myotherstring"));
			for (auto &ptr : ValuesPtrArr)
				MyOtherString.Add(ptr->AsString());

			SomeNumber = JsonObject->GetNumberField(TEXT("somenumber"));

			ROI = sensor_msgs::RegionOfInterest::GetFromJson(JsonObject->GetObjectField(TEXT("roi")));

		}

		static MyCreativeMessage GetFromJson(TSharedPtr<FJsonObject> JsonObject)
		{
			MyCreativeMessage Result;
			Result.FromJson(JsonObject);
			return Result;
		}

		virtual TSharedPtr<FJsonObject> ToJsonObject() const override
		{
			TSharedPtr<FJsonObject> Object = MakeShareable<FJsonObject>(new FJsonObject());

			Object->SetObjectField(TEXT("mystring"), MyString.ToJsonObject());
			TArray<TSharedPtr<FJsonValue>> MyOtherStringArray;
			for (auto &val : MyOtherString)
				MyOtherStringArray.Add(MakeShareable(new FJsonValueString(val)));
			Object->SetArrayField(TEXT("myotherstring"), MyOtherStringArray);
			Object->SetNumberField(TEXT("somenumber"), SomeNumber);
			Object->SetObjectField(TEXT("roi"), ROI.ToJsonObject());
			return Object;
		}
		virtual FString ToYamlString() const override
		{
			FString OutputString;
			TSharedRef< TJsonWriter<> > Writer = TJsonWriterFactory<>::Create(&OutputString);
			FJsonSerializer::Serialize(ToJsonObject().ToSharedRef(), Writer);
			return OutputString;
		}
	};
}