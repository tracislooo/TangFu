$ErrorActionPreference='Stop'
Add-Type -AssemblyName System.Drawing
Add-Type -TypeDefinition @'
using System;
using System.IO;
using System.Drawing;
using System.Drawing.Imaging;
public static class AlphaVerticalProgress {
 public static void Build(string input,string output) {
  Directory.CreateDirectory(output);
  using(var src=new Bitmap(input))
  using(var preview=new Bitmap(680,270))
  using(var g=Graphics.FromImage(preview))
  using(var font=new Font("Arial",12)) {
   if(src.Width!=5 || src.Height!=20) throw new Exception("Unexpected source size");
   g.Clear(Color.FromArgb(238,240,244));
   g.DrawString("Transparent PNG | Bottom to top | 5 x 20 px",font,Brushes.Black,14,12);
   string report="segment,percent,width,height,filled_height,first_filled_y,unchanged_pixels,transparent_upper_area\r\n";
   for(int n=1;n<=9;n++) {
    int height=n*2,top=20-height,count=0;
    using(var dst=new Bitmap(5,20,PixelFormat.Format32bppArgb)) {
     for(int y=top;y<20;y++) for(int x=0;x<5;x++) {
      var c=src.GetPixel(x,y);
      int alpha=c.A;
      if(y<top+2) alpha=Math.Min(alpha,src.GetPixel(x,y-top).A);
      dst.SetPixel(x,y,Color.FromArgb(alpha,c.R,c.G,c.B));
     }
     string path=Path.Combine(output,String.Format("progress_{0:00}_of_10_{1:00}percent.png",n,n*10));
     dst.Save(path,ImageFormat.Png);
     using(var saved=new Bitmap(path)) {
      if(saved.Width!=5 || saved.Height!=20 || !Image.IsAlphaPixelFormat(saved.PixelFormat)) throw new Exception("Format mismatch");
      for(int y=0;y<top;y++) for(int x=0;x<5;x++) if(saved.GetPixel(x,y).A!=0) throw new Exception("Upper area is not transparent");
      for(int y=top;y<20;y++) for(int x=0;x<5;x++) {
       var a=saved.GetPixel(x,y);var b=src.GetPixel(x,y);
       if(a.R!=b.R || a.G!=b.G || a.B!=b.B) throw new Exception("Gradient changed");
       if(y>=top+2) { if(a.ToArgb()!=b.ToArgb()) throw new Exception("Original pixels changed"); count++; }
      }
      for(int x=0;x<5;x++) if(saved.GetPixel(x,19).ToArgb()!=src.GetPixel(x,19).ToArgb()) throw new Exception("Bottom moved");
      if(saved.GetPixel(0,top).A>=saved.GetPixel(2,top).A) throw new Exception("Rounded top missing");
     }
     report+=String.Format("{0},{1},5,20,{2},{3},{4},true\r\n",n,n*10,height,top,count);
     int px=20+(n-1)*73;
     for(int yy=0;yy<20;yy++) for(int xx=0;xx<5;xx++) {
      using(var brush=new SolidBrush((xx+yy)%2==0?Color.White:Color.FromArgb(205,210,218)))
       g.FillRectangle(brush,px+xx*8,54+yy*8,8,8);
     }
     g.InterpolationMode=System.Drawing.Drawing2D.InterpolationMode.NearestNeighbor;
     g.PixelOffsetMode=System.Drawing.Drawing2D.PixelOffsetMode.Half;
     g.DrawImage(dst,new Rectangle(px,54,40,160),0,0,5,20,GraphicsUnit.Pixel);
     g.DrawString((n*10)+"%",font,Brushes.Black,px,226);
    }
   }
   preview.Save(Path.Combine(output,"preview.png"),ImageFormat.Png);
   File.WriteAllText(Path.Combine(output,"verification.csv"),report);
  }
 }
}
'@ -ReferencedAssemblies System.Drawing
[AlphaVerticalProgress]::Build('C:\Users\traci\AppData\Local\Temp\codex-clipboard-792b5d45-9afe-48a1-9585-272d37351492.png','G:\Doc\ChatGPT\New project\竖向进度条-透明PNG-1至9段')
