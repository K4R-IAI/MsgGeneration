#pragma once

#include ROSBridgeMsg.h

#include "std_msgs/Header.h"
#include "sensor_msgs/RegionOfInterest.h"

namespace sensor_msgs
{
	class CameraInfo : public FROSBridgeMsg
	{
		std_msgs::Header Header;
		uint32 Height;
		uint32 Width;
		FString DistortionModel;
		TArray<double> D;
		TArray<double> K;
		TArray<double> R;
		TArray<double> P;
		uint32 BinningX;
		uint32 BinningY;
		sensor_msgs::RegionOfInterest ROI;
	public:
		CameraInfo()
		{
			MsgType = "sensor_msgs/CameraInfo";
		}

		CameraInfo
		(
			std_msgs::Header InHeader,
			uint32 InHeight,
			uint32 InWidth,
			FString InDistortionModel,
			const TArray<double>& InD,
			const TArray<double>& InK,
			const TArray<double>& InR,
			const TArray<double>& InP,
			uint32 InBinningX,
			uint32 InBinningY,
			sensor_msgs::RegionOfInterest InROI
		):
			Header(InHeader),
			Height(InHeight),
			Width(InWidth),
			DistortionModel(InDistortionModel),
			D(InD),
			K(InK),
			R(InR),
			P(InP),
			BinningX(InBinningX),
			BinningY(InBinningY),
			ROI(InROI)
		{
			MsgType = "sensor_msgs/CameraInfo";
		}

		~CameraInfo() override {}

		std_msgs::Header GetHeader() const
		}
			return Header;
		}

		uint32 GetHeight() const
		}
			return Height;
		}

		uint32 GetWidth() const
		}
			return Width;
		}

		FString GetDistortionModel() const
		}
			return DistortionModel;
		}

		TArray<double> GetD() const
		}
			return D;
		}

		TArray<double> GetK() const
		}
			return K;
		}

		TArray<double> GetR() const
		}
			return R;
		}

		TArray<double> GetP() const
		}
			return P;
		}

		uint32 GetBinningX() const
		}
			return BinningX;
		}

		uint32 GetBinningY() const
		}
			return BinningY;
		}

		sensor_msgs::RegionOfInterest GetROI() const
		}
			return ROI;
		}

		void SetHeader(std_msgs::Header InHeader)
		}
			Header = InHeader;
		}

		void SetHeight(uint32 InHeight)
		}
			Height = InHeight;
		}

		void SetWidth(uint32 InWidth)
		}
			Width = InWidth;
		}

		void SetDistortionModel(FString InDistortionModel)
		}
			DistortionModel = InDistortionModel;
		}

		void SetD(TArray<double>& InD)
		}
			D = InD;
		}

		void SetK(TArray<double>& InK)
		}
			K = InK;
		}

		void SetR(TArray<double>& InR)
		}
			R = InR;
		}

		void SetP(TArray<double>& InP)
		}
			P = InP;
		}

		void SetBinningX(uint32 InBinningX)
		}
			BinningX = InBinningX;
		}

		void SetBinningY(uint32 InBinningY)
		}
			BinningY = InBinningY;
		}

		void SetROI(sensor_msgs::RegionOfInterest InROI)
		}
			ROI = InROI;
		}

		virtual void FromJson(TSharedPtr<FJsonObject> JsonObject) override
		{
			Header = std_msgs::Header::GetFromJson(JsonObject->GetObjectField(TEXT("header")));

			Height = JsonObject->GetNumberField(TEXT("height"));

			Width = JsonObject->GetNumberField(TEXT("width"));

			DistortionModel = JsonObject->GetStringField(TEXT("distortionmodel"));

			TArray<TSharedPtr<FJsonValue>> ValuesPtrArr;

			D.Empty();
			ValuesPtrArr = JsonObject->GetArrayField(TEXT("d"));
			for (auto &ptr : ValuesPtrArr)
				D.Add(ptr->AsNumber());

			K.Empty();
			ValuesPtrArr = JsonObject->GetArrayField(TEXT("k"));
			for (auto &ptr : ValuesPtrArr)
				K.Add(ptr->AsNumber());

			R.Empty();
			ValuesPtrArr = JsonObject->GetArrayField(TEXT("r"));
			for (auto &ptr : ValuesPtrArr)
				R.Add(ptr->AsNumber());

			P.Empty();
			ValuesPtrArr = JsonObject->GetArrayField(TEXT("p"));
			for (auto &ptr : ValuesPtrArr)
				P.Add(ptr->AsNumber());

			BinningX = JsonObject->GetNumberField(TEXT("binningx"));

			BinningY = JsonObject->GetNumberField(TEXT("binningy"));

			ROI = sensor_msgs::RegionOfInterest::GetFromJson(JsonObject->GetObjectField(TEXT("roi")));

		}

		static CameraInfo GetFromJson(TSharedPtr<FJsonObject> JsonObject)
		{
			CameraInfo Result;
			Result.FromJson(JsonObject);
			return Result;
		}

		virtual TSharedPtr<FJsonObject> ToJsonObject() const override
		{
			TSharedPtr<FJsonObject> Object = MakeShareable<FJsonObject>(new FJsonObject());

			Object->SetObjectField(TEXT("header"), Header.ToJsonObject());
			Object->SetNumberField(TEXT("height"), Height);
			Object->SetNumberField(TEXT("width"), Width);
			Object->SetStringField(TEXT("distortionmodel"), DistortionModel);
			TArray<TSharedPtr<FJsonValue>> DArray;
			for (auto &val : D)
				DArray.Add(MakeShareable(new FJsonValueNumber(val)));
			Object->SetArrayField(TEXT("d"), DArray);
			TArray<TSharedPtr<FJsonValue>> KArray;
			for (auto &val : K)
				KArray.Add(MakeShareable(new FJsonValueNumber(val)));
			Object->SetArrayField(TEXT("k"), KArray);
			TArray<TSharedPtr<FJsonValue>> RArray;
			for (auto &val : R)
				RArray.Add(MakeShareable(new FJsonValueNumber(val)));
			Object->SetArrayField(TEXT("r"), RArray);
			TArray<TSharedPtr<FJsonValue>> PArray;
			for (auto &val : P)
				PArray.Add(MakeShareable(new FJsonValueNumber(val)));
			Object->SetArrayField(TEXT("p"), PArray);
			Object->SetNumberField(TEXT("binningx"), BinningX);
			Object->SetNumberField(TEXT("binningy"), BinningY);
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