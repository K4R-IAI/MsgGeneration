#pragma once

#include "ROSBridgeMsg.h"

#include "std_msgs/Header.h"
#include "sensor_msgs/RegionOfInterest.h"

namespace test_package
{
	class CameraInfo : public FROSBridgeMsg
	{
		std_msgs::Header header;
		uint32 height;
		uint32 width;
		FString DistortionModel;
		TArray<double> d;
		TArray<double> k;
		TArray<double> r;
		TArray<double> p;
		uint32 BinningX;
		uint32 BinningY;
		sensor_msgs::RegionOfInterest roi;
	public:
		CameraInfo()
		{
			MsgType = "test_package/CameraInfo";
		}

		CameraInfo
		(
			std_msgs::Header Inheader,
			uint32 Inheight,
			uint32 Inwidth,
			FString InDistortionModel,
			const TArray<double>& Ind,
			const TArray<double>& Ink,
			const TArray<double>& Inr,
			const TArray<double>& Inp,
			uint32 InBinningX,
			uint32 InBinningY,
			sensor_msgs::RegionOfInterest Inroi
		):
			header(Inheader),
			height(Inheight),
			width(Inwidth),
			DistortionModel(InDistortionModel),
			d(Ind),
			k(Ink),
			r(Inr),
			p(Inp),
			BinningX(InBinningX),
			BinningY(InBinningY),
			roi(Inroi)
		{
			MsgType = "test_package/CameraInfo";
		}

		~CameraInfo() override {}

		std_msgs::Header Getheader() const
		}
			return header;
		}

		uint32 Getheight() const
		}
			return height;
		}

		uint32 Getwidth() const
		}
			return width;
		}

		FString GetDistortionModel() const
		}
			return DistortionModel;
		}

		TArray<double> Getd() const
		}
			return d;
		}

		TArray<double> Getk() const
		}
			return k;
		}

		TArray<double> Getr() const
		}
			return r;
		}

		TArray<double> Getp() const
		}
			return p;
		}

		uint32 GetBinningX() const
		}
			return BinningX;
		}

		uint32 GetBinningY() const
		}
			return BinningY;
		}

		sensor_msgs::RegionOfInterest Getroi() const
		}
			return roi;
		}

		void Setheader(std_msgs::Header Inheader)
		}
			header = Inheader;
		}

		void Setheight(uint32 Inheight)
		}
			height = Inheight;
		}

		void Setwidth(uint32 Inwidth)
		}
			width = Inwidth;
		}

		void SetDistortionModel(FString InDistortionModel)
		}
			DistortionModel = InDistortionModel;
		}

		void Setd(TArray<double>& Ind)
		}
			d = Ind;
		}

		void Setk(TArray<double>& Ink)
		}
			k = Ink;
		}

		void Setr(TArray<double>& Inr)
		}
			r = Inr;
		}

		void Setp(TArray<double>& Inp)
		}
			p = Inp;
		}

		void SetBinningX(uint32 InBinningX)
		}
			BinningX = InBinningX;
		}

		void SetBinningY(uint32 InBinningY)
		}
			BinningY = InBinningY;
		}

		void Setroi(sensor_msgs::RegionOfInterest Inroi)
		}
			roi = Inroi;
		}

		virtual void FromJson(TSharedPtr<FJsonObject> JsonObject) override
		{
			header = std_msgs::Header::GetFromJson(JsonObject->GetObjectField(TEXT("header")));

			height = JsonObject->GetNumberField(TEXT("height"));

			width = JsonObject->GetNumberField(TEXT("width"));

			DistortionModel = JsonObject->GetStringField(TEXT("distortion_model"));

			TArray<TSharedPtr<FJsonValue>> ValuesPtrArr;

			d.Empty();
			ValuesPtrArr = JsonObject->GetArrayField(TEXT("d"));
			for (auto &ptr : ValuesPtrArr)
				d.Add(ptr->AsNumber());

			k.Empty();
			ValuesPtrArr = JsonObject->GetArrayField(TEXT("k"));
			for (auto &ptr : ValuesPtrArr)
				k.Add(ptr->AsNumber());

			r.Empty();
			ValuesPtrArr = JsonObject->GetArrayField(TEXT("r"));
			for (auto &ptr : ValuesPtrArr)
				r.Add(ptr->AsNumber());

			p.Empty();
			ValuesPtrArr = JsonObject->GetArrayField(TEXT("p"));
			for (auto &ptr : ValuesPtrArr)
				p.Add(ptr->AsNumber());

			BinningX = JsonObject->GetNumberField(TEXT("binning_x"));

			BinningY = JsonObject->GetNumberField(TEXT("binning_y"));

			roi = sensor_msgs::RegionOfInterest::GetFromJson(JsonObject->GetObjectField(TEXT("roi")));

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

			Object->SetObjectField(TEXT("header"), header.ToJsonObject());
			Object->SetNumberField(TEXT("height"), height);
			Object->SetNumberField(TEXT("width"), width);
			Object->SetStringField(TEXT("distortion_model"), DistortionModel);
			TArray<TSharedPtr<FJsonValue>> dArray;
			for (auto &val : d)
				dArray.Add(MakeShareable(new FJsonValueNumber(val)));
			Object->SetArrayField(TEXT("d"), dArray);
			TArray<TSharedPtr<FJsonValue>> kArray;
			for (auto &val : k)
				kArray.Add(MakeShareable(new FJsonValueNumber(val)));
			Object->SetArrayField(TEXT("k"), kArray);
			TArray<TSharedPtr<FJsonValue>> rArray;
			for (auto &val : r)
				rArray.Add(MakeShareable(new FJsonValueNumber(val)));
			Object->SetArrayField(TEXT("r"), rArray);
			TArray<TSharedPtr<FJsonValue>> pArray;
			for (auto &val : p)
				pArray.Add(MakeShareable(new FJsonValueNumber(val)));
			Object->SetArrayField(TEXT("p"), pArray);
			Object->SetNumberField(TEXT("binning_x"), BinningX);
			Object->SetNumberField(TEXT("binning_y"), BinningY);
			Object->SetObjectField(TEXT("roi"), roi.ToJsonObject());
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